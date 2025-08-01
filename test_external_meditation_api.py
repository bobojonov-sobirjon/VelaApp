#!/usr/bin/env python3
"""
Test script for external meditation API integration
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.services import ExternalMeditationService
from apps.accounts.models import CustomUser

def test_external_meditation_api():
    """Test the external meditation API integration"""
    
    # Create a test user
    user, created = CustomUser.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Test data
    test_data = {
        "plan_type": "Morning Spark",
        "gender": "male",
        "dream": "Wake up in a hammock enveloped within nature, with a waterfall in the background",
        "goals": "Enjoy life to the Fullest. Make vela an Editor's Choice Wellness app in the AppStore",
        "age_range": "25",
        "happiness": "Adventure, Beauty, Nature, Creation. I feel most me when I'm building something that matters.",
        "ritual_type": "story",
        "tone": "dreamy",
        "voice": "female",
        "duration": "2"
    }
    
    # Initialize service
    service = ExternalMeditationService()
    
    print("Testing external meditation API integration...")
    print(f"Test data: {test_data}")
    print(f"External API enabled: {getattr(settings, 'MEDITATION_API_CONFIG', {}).get('ENABLED', True)}")
    
    try:
        # Process meditation request
        result = service.process_meditation_request(user, test_data)
        
        print(f"\nResult: {result}")
        
        if result.get('success'):
            print("✅ Test passed - Meditation record created successfully")
        else:
            print(f"⚠️ Test completed with fallback - {result.get('error', 'Unknown error')}")
            
        if result.get('fallback_used'):
            print("ℹ️ Fallback mechanism was used (external API unavailable)")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_external_meditation_api() 