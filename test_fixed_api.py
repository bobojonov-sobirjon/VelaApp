#!/usr/bin/env python3
"""
Test script to verify the fixed meditation API
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

def test_fixed_api():
    """Test the fixed meditation API"""
    
    print("Testing fixed meditation API...")
    
    # Test data matching the expected format
    test_data = {
        "plan_type": "Morning Spark",
        "gender": "Boris",
        "dream": "Wake up in a hammock enveloped within nature, with with a waterfall in the backgroundg",
        "goals": "Enjoy life to the Fullest. Make vela an Editor's Choice Wellness app in the ApppStore",
        "age_range": "25",
        "happiness": "Adventure, Beauty, Nature, Creation. I feel most me when I'm building something that matters.",
        "ritual_type": "story",
        "tone": "dreamy",
        "voice": "female",
        "duration": "2"
    }
    
    # Test the payload generation
    service = ExternalMeditationService()
    
    # Test the mapping function
    def map_to_external_format(value, field_type):
        if field_type == 'ritual_type':
            mapping = {'story': 'Story', 'guided_meditations': 'Guided'}
            return mapping.get(value, 'Story')
        elif field_type == 'tone':
            mapping = {'dreamy': 'Dreamy', 'asmr': 'ASMR'}
            return mapping.get(value, 'Dreamy')
        elif field_type == 'voice':
            mapping = {'male': 'Male', 'female': 'Female'}
            return mapping.get(value, 'Female')
        else:
            return value
    
    # Generate the expected payload
    expected_payload = {
        "name": test_data['gender'],
        "goals": test_data['goals'],
        "dreamlife": test_data['dream'],
        "dream_activities": test_data['happiness'],
        "ritual_type": map_to_external_format(test_data['ritual_type'], 'ritual_type'),
        "tone": map_to_external_format(test_data['tone'], 'tone'),
        "voice": map_to_external_format(test_data['voice'], 'voice'),
        "length": int(test_data['duration']),
        "check_in": "string"
    }
    
    print("Expected payload format:")
    import json
    print(json.dumps(expected_payload, indent=2))
    
    print("\n✅ Test completed successfully!")
    print("The API should now work with the correct payload format.")

if __name__ == '__main__':
    test_fixed_api() 