import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    TOOLTRACKER_DB = os.environ.get('TOOLTRACKER_DB', 'tooltracker.db')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join('static', 'images'))
    
    # OIDC Configuration
    OIDC_CLIENT_ID = os.environ.get('OIDC_CLIENT_ID')
    OIDC_CLIENT_SECRET = os.environ.get('OIDC_CLIENT_SECRET')
    OIDC_DISCOVERY_URL = os.environ.get('OIDC_DISCOVERY_URL')
    OIDC_ISSUER = os.environ.get('OIDC_ISSUER')
    OIDC_SCOPES = os.environ.get('OIDC_SCOPES', 'openid profile email')
    
    # Custom OIDC endpoints (if not using discovery)
    OIDC_AUTHORIZATION_ENDPOINT = os.environ.get('OIDC_AUTHORIZATION_ENDPOINT')
    OIDC_TOKEN_ENDPOINT = os.environ.get('OIDC_TOKEN_ENDPOINT')
    OIDC_USERINFO_ENDPOINT = os.environ.get('OIDC_USERINFO_ENDPOINT')
    
    # Application Configuration
    APP_NAME = os.environ.get('APP_NAME', 'Tool Tracker')
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
    
    # OIDC Redirect URI - REQUIRED for proper Authentik integration
    OIDC_REDIRECT_URI = os.environ.get('OIDC_REDIRECT_URI')
    if not OIDC_REDIRECT_URI:
        raise ValueError("OIDC_REDIRECT_URI environment variable is required. Set it to your full callback URL (e.g., https://yourdomain.com/oidc/callback)")

    # Image optimization constants
    MAX_IMAGE_DIMENSION = 1024
    JPEG_QUALITY = 85
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
