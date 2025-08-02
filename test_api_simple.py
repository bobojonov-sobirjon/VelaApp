#!/usr/bin/env python3
"""
Simple test script for external meditation API
"""
import requests
import json

def test_external_meditation_api():
    """Test the external meditation API with a simple request"""
    
    # API endpoint
    url = "http://localhost:8000/api/auth/meditation/external/"
    
    # Test data - using plan_type ID 1 (assuming it exists)
    test_data = {
        "plan_type": 1,  # This should be a valid RitualType ID
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
    
    print("Testing external meditation API...")
    print(f"URL: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make the request
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the Django server is running")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == '__main__':
    test_external_meditation_api() 