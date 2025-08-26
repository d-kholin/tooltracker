# OIDC Authentication Setup Guide

This guide will help you set up OpenID Connect (OIDC) authentication for your Tool Tracker application.

## Prerequisites

- Python 3.7+
- An OIDC identity provider (e.g., Auth0, Okta, Keycloak, Azure AD, etc.)
- A registered OAuth 2.0 application with your identity provider

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Copy the environment file and configure it:
```bash
cp env.example .env
```

3. Edit the `.env` file with your OIDC configuration.

## OIDC Configuration

### Environment Variables

Set the following variables in your `.env` file:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
TOOLTRACKER_DB=tooltracker.db
UPLOAD_FOLDER=static/images

# OIDC Configuration
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_DISCOVERY_URL=https://your-identity-provider/.well-known/openid_configuration
OIDC_ISSUER=https://your-identity-provider
OIDC_SCOPES=openid profile email

# Application Configuration
APP_NAME=Tool Tracker
APP_URL=http://localhost:5000
```

### Identity Provider Setup

#### Auth0 Example
1. Create an Auth0 account and application
2. Set the following in your Auth0 application:
   - **Allowed Callback URLs**: `http://localhost:5000/oidc/callback`
   - **Allowed Logout URLs**: `http://localhost:5000`
   - **Application Type**: Regular Web Application
3. Copy the Client ID and Client Secret to your `.env` file
4. Set `OIDC_DISCOVERY_URL` to: `https://your-tenant.auth0.com/.well-known/openid_configuration`

#### Okta Example
1. Create an Okta developer account and application
2. Set the following in your Okta application:
   - **Base URIs**: `http://localhost:5000`
   - **Login redirect URIs**: `http://localhost:5000/oidc/callback`
   - **Application type**: Web
3. Copy the Client ID and Client Secret to your `.env` file
4. Set `OIDC_DISCOVERY_URL` to: `https://your-domain.okta.com/.well-known/openid_configuration`

#### Keycloak Example
1. Set up a Keycloak server
2. Create a new realm and client
3. Set the following in your Keycloak client:
   - **Client ID**: Your chosen client ID
   - **Valid Redirect URIs**: `http://localhost:5000/oidc/callback`
   - **Access Type**: confidential
4. Copy the Client ID and Client Secret to your `.env` file
5. Set `OIDC_DISCOVERY_URL` to: `http://your-keycloak-server/auth/realms/your-realm/.well-known/openid_configuration`

## Running the Application

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`
3. You will be redirected to the login page
4. Click "Sign In with OIDC" to authenticate with your identity provider

## Features

### Multi-User Support
- Each user gets their own account automatically created on first login
- Users can only see and manage their own tools and people
- All actions are tracked with user attribution

### Security Features
- CSRF protection with state parameter
- Secure session management
- OAuth 2.0 authorization code flow
- Automatic user creation and management

### Database Schema Updates
The application automatically updates the database schema to include:
- `users` table for authentication
- `created_by` fields in tools and people tables
- `lent_by` field in loans table
- Foreign key relationships to maintain data integrity

## Troubleshooting

### Common Issues

1. **"OIDC authentication not configured properly"**
   - Check that all OIDC environment variables are set
   - Verify your Client ID and Client Secret are correct

2. **"Failed to discover OIDC configuration"**
   - Check your discovery URL is accessible
   - Verify your identity provider supports OIDC discovery

3. **"Invalid state parameter"**
   - This usually indicates a CSRF attack or session issue
   - Clear your browser cookies and try again

4. **"Failed to obtain access token"**
   - Check your redirect URI matches exactly
   - Verify your Client Secret is correct
   - Ensure your application is configured for the authorization code flow

### Debug Mode
Enable debug mode by setting `FLASK_DEBUG=1` in your `.env` file to see detailed error messages.

### Logs
Check the application logs for detailed error information when troubleshooting authentication issues.

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Use a strong, unique `SECRET_KEY`
3. Set `FLASK_DEBUG=0`
4. Use HTTPS for all OIDC callbacks
5. Update your identity provider configuration with production URLs
6. Consider using environment-specific configuration files

## Support

If you encounter issues:
1. Check the application logs
2. Verify your OIDC configuration
3. Test with a simple OIDC client first
4. Consult your identity provider's documentation
