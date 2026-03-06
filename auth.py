import os
import sqlite3
import time
from functools import wraps
from flask import Flask, request, redirect, url_for, session, flash, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from config import Config

class User(UserMixin):
    """User model for Flask-Login"""
    
    def __init__(self, user_id, email, name, picture=None):
        self.id = user_id
        self.email = email
        self.name = name
        self.picture = picture
    
    @staticmethod
    def get(user_id):
        """Get user by ID from database"""
        with get_auth_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = c.fetchone()
            if user_data:
                return User(
                    user_id=user_data['id'],
                    email=user_data['email'],
                    name=user_data['name'],
                    picture=user_data['picture']
                )
        return None

def get_auth_conn(app=None):
    """Get database connection for authentication"""
    if app is None:
        app = current_app
    db_path = app.config.get('TOOLTRACKER_DB', 'tooltracker.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db(app=None):
    """Initialize authentication database tables"""
    with get_auth_conn(app) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

OIDC_DISCOVERY_TIMEOUT = 5  # seconds
OIDC_RETRY_COOLDOWN = 60    # seconds between retry attempts after failure


class OIDCAuth:
    """OIDC Authentication handler"""

    def __init__(self, app):
        self.app = app
        self.client = None
        self.oidc_config = None
        self._last_setup_attempt = 0
        self.setup_oidc()
    
    def setup_oidc(self):
        """Setup OIDC client and configuration"""
        self._last_setup_attempt = time.monotonic()
        if not self.app.config.get('OIDC_CLIENT_ID'):
            self.app.logger.warning("OIDC_CLIENT_ID not configured, authentication disabled")
            return
        
        if not self.app.config.get('OIDC_REDIRECT_URI'):
            self.app.logger.error("OIDC_REDIRECT_URI not configured, authentication disabled")
            return
        
        self.app.logger.info(f"Setting up OIDC with client_id: {self.app.config['OIDC_CLIENT_ID']}")
        self.app.logger.info(f"Client secret configured: {'Yes' if self.app.config.get('OIDC_CLIENT_SECRET') else 'No'}")
        
        self.client = WebApplicationClient(self.app.config['OIDC_CLIENT_ID'])
        
        # Try to discover OIDC configuration
        if self.app.config.get('OIDC_DISCOVERY_URL'):
            try:
                self.app.logger.info(f"Attempting OIDC discovery at: {self.app.config['OIDC_DISCOVERY_URL']}")
                resp = requests.get(self.app.config['OIDC_DISCOVERY_URL'], timeout=OIDC_DISCOVERY_TIMEOUT)
                resp.raise_for_status()
                self.oidc_config = resp.json()
                self.app.logger.info("OIDC configuration discovered successfully")
                self.app.logger.info(f"Token endpoint: {self.oidc_config.get('token_endpoint')}")
            except Exception as e:
                self.app.logger.error(f"Failed to discover OIDC configuration: {e}")
                self.oidc_config = None
        
        # Use custom endpoints if discovery failed or not configured
        if not self.oidc_config:
            self.app.logger.info("Using custom OIDC endpoints")
            self.oidc_config = {
                'authorization_endpoint': self.app.config.get('OIDC_AUTHORIZATION_ENDPOINT'),
                'token_endpoint': self.app.config.get('OIDC_TOKEN_ENDPOINT'),
                'userinfo_endpoint': self.app.config.get('OIDC_USERINFO_ENDPOINT'),
                'issuer': self.app.config.get('OIDC_ISSUER')
            }
            self.app.logger.info(f"Custom token endpoint: {self.oidc_config.get('token_endpoint')}")

        # Validate that required endpoints are present
        required = ('authorization_endpoint', 'token_endpoint', 'userinfo_endpoint')
        if not all(self.oidc_config.get(k) for k in required):
            missing = [k for k in required if not self.oidc_config.get(k)]
            self.app.logger.error(
                f"OIDC configuration incomplete — missing endpoints: {missing}. "
                "Set OIDC_DISCOVERY_URL or individual OIDC_*_ENDPOINT vars."
            )
            self.oidc_config = None
    
    def get_authorization_url(self, redirect_uri, state):
        """Get authorization URL for OIDC login"""
        # Retry OIDC setup if a previous attempt failed, but at most once per cooldown period
        if not self.oidc_config and self.app.config.get('OIDC_DISCOVERY_URL'):
            elapsed = time.monotonic() - self._last_setup_attempt
            if elapsed >= OIDC_RETRY_COOLDOWN:
                self.app.logger.info("Retrying OIDC discovery after previous failure")
                self.setup_oidc()
            else:
                self.app.logger.warning(
                    f"OIDC not configured — retry in {int(OIDC_RETRY_COOLDOWN - elapsed)}s"
                )

        endpoint = self.oidc_config.get('authorization_endpoint') if self.oidc_config else None
        if not self.client or not endpoint:
            self.app.logger.error("OIDC authorization endpoint not configured")
            return None

        scopes = self.app.config.get('OIDC_SCOPES', 'openid profile email')
        self.app.logger.info(f'OIDC authorization endpoint: {endpoint}')
        self.app.logger.info(f'OIDC redirect_uri input: {redirect_uri}')
        self.app.logger.info(f'OIDC scopes: {scopes}')
        self.app.logger.info(f'OIDC state: {state}')

        auth_url = self.client.prepare_request_uri(
            endpoint,
            redirect_uri=redirect_uri,
            scope=scopes,
            state=state
        )
        
        self.app.logger.info(f'OIDC generated auth URL: {auth_url}')
        return auth_url
    
    def get_token(self, authorization_response, redirect_uri):
        """Exchange authorization code for tokens"""
        if not self.client or not self.oidc_config:
            return None
        
        # Extract the authorization code from the response URL
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(authorization_response)
        query_params = parse_qs(parsed_url.query)
        code = query_params.get('code', [None])[0]
        
        if not code:
            self.app.logger.error("No authorization code found in response")
            return None
        
        token_url = self.oidc_config['token_endpoint']
        
        # Prepare the token request data
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.app.config['OIDC_CLIENT_ID'],
        }
        
        # Add client secret if configured
        if self.app.config.get('OIDC_CLIENT_SECRET'):
            token_data['client_secret'] = self.app.config['OIDC_CLIENT_SECRET']
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        self.app.logger.info(f"Token exchange request to: {token_url}")
        
        try:
            resp = requests.post(token_url, data=token_data, headers=headers)
            self.app.logger.info(f"Token exchange response status: {resp.status_code}")
            self.app.logger.info(f"Token exchange response headers: {dict(resp.headers)}")
            
            if resp.status_code != 200:
                self.app.logger.error(f"Token exchange failed with status {resp.status_code}")
                self.app.logger.error(f"Response content: {resp.text}")
            
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            self.app.logger.error(f"Token exchange failed: {e}")
            self.app.logger.error(f"Response content: {resp.text}")
            raise
    
    def get_userinfo(self, access_token):
        """Get user information from OIDC provider"""
        if not self.oidc_config or not self.oidc_config.get('userinfo_endpoint'):
            return None
        
        headers = {'Authorization': f'Bearer {access_token}'}
        resp = requests.get(self.oidc_config['userinfo_endpoint'], headers=headers)
        resp.raise_for_status()
        return resp.json()

def create_or_update_user(userinfo):
    """Create or update user in database"""
    user_id = userinfo.get('sub') or userinfo.get('id')
    email = userinfo.get('email')
    name = userinfo.get('name') or userinfo.get('preferred_username') or email
    picture = userinfo.get('picture')
    
    if not user_id or not email:
        return None
    
    with get_auth_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO users (id, email, name, picture, last_login)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, email, name, picture))
        conn.commit()
    
    return User(user_id, email, name, picture)

def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Add admin check logic here if needed
        return f(*args, **kwargs)
    return decorated_function
