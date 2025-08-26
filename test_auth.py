#!/usr/bin/env python3
"""
Test script to verify OIDC authentication configuration
"""

import os
from dotenv import load_dotenv

def test_config():
    """Test that all required configuration is present"""
    load_dotenv()
    
    print("🔍 Testing OIDC Authentication Configuration...")
    print("=" * 50)
    
    # Required OIDC variables
    required_vars = [
        'OIDC_CLIENT_ID',
        'OIDC_CLIENT_SECRET',
        'OIDC_DISCOVERY_URL',
        'OIDC_ISSUER'
    ]
    
    # Optional variables
    optional_vars = [
        'OIDC_AUTHORIZATION_ENDPOINT',
        'OIDC_TOKEN_ENDPOINT',
        'OIDC_USERINFO_ENDPOINT',
        'OIDC_SCOPES'
    ]
    
    # Test required variables
    missing_required = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (configured)")
        else:
            print(f"❌ {var}: NOT SET")
            missing_required.append(var)
    
    print()
    
    # Test optional variables
    print("Optional OIDC Configuration:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (configured)")
        else:
            print(f"⚠️  {var}: NOT SET (will use discovery)")
    
    print()
    
    # Test other configuration
    print("Other Configuration:")
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key and secret_key != 'your-secret-key-here':
        print(f"✅ SECRET_KEY: {'*' * len(secret_key)} (configured)")
    else:
        print(f"⚠️  SECRET_KEY: Using default (not recommended for production)")
    
    app_name = os.environ.get('APP_NAME', 'Tool Tracker')
    print(f"✅ APP_NAME: {app_name}")
    
    app_url = os.environ.get('APP_URL', 'http://localhost:5000')
    print(f"✅ APP_URL: {app_url}")
    
    print()
    
    # Summary
    if missing_required:
        print("❌ Configuration incomplete!")
        print(f"Missing required variables: {', '.join(missing_required)}")
        print("\nPlease set these variables in your .env file.")
        return False
    else:
        print("✅ All required OIDC configuration is present!")
        print("\nYou can now run the application with:")
        print("python app.py")
        return True

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing package imports...")
    print("=" * 50)
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_login
        print("✅ Flask-Login imported successfully")
    except ImportError as e:
        print(f"❌ Flask-Login import failed: {e}")
        return False
    
    try:
        from oauthlib.oauth2 import WebApplicationClient
        print("✅ OAuthLib imported successfully")
    except ImportError as e:
        print(f"❌ OAuthLib import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        return False
    
    print()
    return True

if __name__ == "__main__":
    print("🚀 Tool Tracker Authentication Test")
    print("=" * 50)
    print()
    
    # Test imports first
    if not test_imports():
        print("\n❌ Package import test failed!")
        print("Please install missing packages with: pip install -r requirements.txt")
        exit(1)
    
    print()
    
    # Test configuration
    if test_config():
        print("\n🎉 All tests passed! Your authentication is ready to use.")
    else:
        print("\n💡 Configuration test failed. Please check the issues above.")
        exit(1)
