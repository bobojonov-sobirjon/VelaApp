#!/usr/bin/env python3
"""
Test script for the new meditation API request format
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8080"  # Change this to your server URL
API_ENDPOINT = f"{BASE_URL}/api/auth/meditation/external/"

# Test data with the new format
test_data = {
    "plan_type": 4746,
    "gender": "male",
    "dream": "string",
    "goals": "string",
    "age_range": "string",
    "happiness": "string",
    "ritual_type": "guided_meditations",
    "tone": "dreamy",
    "voice": "male",
    "duration": "10"
}

def test_new_meditation_format():
    """Test the new meditation API request format"""
    
    print("🧪 Testing New Meditation API Format")
    print("=" * 50)
    
    # Print the request data
    print(f"📤 Request URL: {API_ENDPOINT}")
    print(f"📤 Request Data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        # Make the API request
        response = requests.post(
            API_ENDPOINT,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_TOKEN_HERE'  # Replace with actual token
            },
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            response_data = response.json()
            print("📥 Response Data:")
            print(json.dumps(response_data, indent=2))
        else:
            print("❌ FAILED!")
            print(f"📥 Error Response:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

def test_invalid_keys():
    """Test with invalid keys to ensure validation works"""
    
    print("\n🧪 Testing Invalid Keys")
    print("=" * 50)
    
    invalid_data = {
        "plan_type": 4746,
        "gender": "male",
        "dream": "string",
        "goals": "string",
        "age_range": "string",
        "happiness": "string",
        "ritual_type": "invalid_key",  # Invalid key
        "tone": "invalid_tone",        # Invalid key
        "voice": "invalid_voice",      # Invalid key
        "duration": "invalid_duration"  # Invalid key
    }
    
    print(f"📤 Invalid Request Data:")
    print(json.dumps(invalid_data, indent=2))
    print()
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=invalid_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_TOKEN_HERE'  # Replace with actual token
            },
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Validation working correctly!")
            print(f"📥 Error Response:")
            print(response.text)
        else:
            print("❌ Expected 400 status for invalid keys")
            print(f"📥 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Meditation API Tests")
    print("=" * 50)
    
    # Test valid format
    test_new_meditation_format()
    
    # Test invalid keys
    test_invalid_keys()
    
    print("\n✅ Tests completed!") 