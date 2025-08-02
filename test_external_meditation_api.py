#!/usr/bin/env python3
"""
Test script for External Meditation API
Tests the API with the new request format
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:8000/meditation/external/"

# Test data matching the new format
test_data = {
    "plan_type": 2,
    "gender": "male",
    "dream": "Wake up in a hammock enveloped within nature, with with a waterfall in the backgroundg",
    "goals": "Enjoy life to the Fullest. Make vela an Editor's Choice Wellness app in the ApppStore",
    "age_range": "25",
    "happiness": "Adventure, Beauty, Nature, Creation. I feel most me when I'm building something that matters.",
    "ritual_type": "story",
    "tone": "dreamy",
    "voice": "female",
    "duration": "2"
}

def test_external_meditation_api():
    """Test the external meditation API"""
    print("Testing External Meditation API...")
    print(f"Request URL: {API_URL}")
    print(f"Request Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        # Make the request
        response = requests.post(
            API_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Success!")
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
            
            # Check for required fields
            required_fields = ['success', 'message', 'plan_type', 'ritual_type_name']
            for field in required_fields:
                if field in response_data:
                    print(f"✅ {field}: {response_data[field]}")
                else:
                    print(f"❌ Missing field: {field}")
            
            # Check for file URL
            if 'file_url' in response_data and response_data['file_url']:
                print(f"✅ File URL: {response_data['file_url']}")
            else:
                print("⚠️ No file URL in response")
                
            # Check for meditation ID
            if 'meditation_id' in response_data:
                print(f"✅ Meditation ID: {response_data['meditation_id']}")
            else:
                print("❌ Missing meditation_id")
                
        else:
            print("❌ Request failed!")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_external_meditation_api() 