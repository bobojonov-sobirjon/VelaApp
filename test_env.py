#!/usr/bin/env python
"""
Test script to verify environment variables are loading correctly
Run this script to check if your .env file is working properly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django settings
from django.conf import settings

def test_environment_variables():
    """Test if environment variables are loaded correctly"""
    
    print("🔍 Testing Environment Variables...")
    print("=" * 50)
    
    # Test Google OAuth settings
    print(f"Google Client ID: {'✅ Set' if settings.GOOGLE_CLIENT_ID else '❌ Empty'}")
    print(f"Google Client Secret: {'✅ Set' if settings.GOOGLE_CLIENT_SECRET else '❌ Empty'}")
    print(f"Google Redirect URI: {'✅ Set' if settings.GOOGLE_REDIRECT_URI else '❌ Empty'}")
    
    print()
    
    # Test Facebook OAuth settings
    print(f"Facebook App ID: {'✅ Set' if settings.FACEBOOK_APP_ID else '❌ Empty'}")
    print(f"Facebook App Secret: {'✅ Set' if settings.FACEBOOK_APP_SECRET else '❌ Empty'}")
    print(f"Facebook Redirect URI: {'✅ Set' if settings.FACEBOOK_REDIRECT_URI else '❌ Empty'}")
    
    print()
    
    # Test Apple ID settings
    print(f"Apple Client ID: {'✅ Set' if settings.APPLE_CLIENT_ID else '❌ Empty'}")
    print(f"Apple Team ID: {'✅ Set' if settings.APPLE_TEAM_ID else '❌ Empty'}")
    print(f"Apple Key ID: {'✅ Set' if settings.APPLE_KEY_ID else '❌ Empty'}")
    print(f"Apple Private Key: {'✅ Set' if settings.APPLE_PRIVATE_KEY else '❌ Empty'}")
    
    print()
    print("=" * 50)
    
    # Check if .env file exists
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file_path):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Please create a .env file in your project root")
    
    print()
    
    # Summary
    google_configured = all([settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_REDIRECT_URI])
    facebook_configured = all([settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, settings.FACEBOOK_REDIRECT_URI])
    apple_configured = all([settings.APPLE_CLIENT_ID, settings.APPLE_TEAM_ID, settings.APPLE_KEY_ID, settings.APPLE_PRIVATE_KEY])
    
    print("📊 Configuration Summary:")
    print(f"Google OAuth: {'✅ Ready' if google_configured else '❌ Not Ready'}")
    print(f"Facebook OAuth: {'✅ Ready' if facebook_configured else '❌ Not Ready'}")
    print(f"Apple ID: {'✅ Ready' if apple_configured else '❌ Not Ready'}")
    
    if not any([google_configured, facebook_configured, apple_configured]):
        print("\n⚠️  No OAuth providers are configured!")
        print("   Please follow the instructions in ENV_SETUP.md to configure your OAuth providers.")

if __name__ == "__main__":
    test_environment_variables() 