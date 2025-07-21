#!/usr/bin/env python3
"""
Test script for meditation API integration
"""
import requests
import json
from datetime import datetime

# API endpoints
api_endpoints = {
    "Sleep Manifestation": "http://31.97.98.47:8000/sleep",
    "Morning Spark": "http://31.97.98.47:8000/spark", 
    "Calming Reset": "http://31.97.98.47:8000/calm",
    "Dream Visualizer": "http://31.97.98.47:8000/dream"
}

def test_meditation_api(plan_type_name, api_url):
    """Test a specific meditation API endpoint"""
    print(f"\nTesting {plan_type_name} API: {api_url}")
    
    # Sample payload
    payload = {
        "name": "Test Meditation",
        "goals": "Start a morning routine, feel less anxious, travel more.",
        "dreamlife": "I'm living in a cozy home filled with art, waking up feeling calm, working on projects that light me up. What makes you happy: I feel most myself when I laugh freely, make art, and spend time in nature.",
        "dream_activities": "string",
        "ritual_type": "Story",
        "tone": "Dreamy",
        "voice": "Female",
        "length": 2,
        "check_in": "string"
    }
    
    try:
        print(f"Sending POST request with payload: {json.dumps(payload, indent=2)}")
        
        # Make POST request to the API
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Check if response contains audio data
            content_type = response.headers.get('content-type', '')
            print(f"Content-Type: {content_type}")
            
            if content_type.startswith('audio/'):
                # Create a filename for the meditation
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_meditation_{plan_type_name.lower().replace(' ', '_')}_{timestamp}.mp3"
                
                # Save the audio file
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Success! Audio file saved as: {filename}")
                print(f"File size: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ API did not return audio content. Response: {response.text[:200]}...")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Test all meditation APIs"""
    print("Testing Meditation API Integration")
    print("=" * 50)
    
    results = {}
    
    for plan_type_name, api_url in api_endpoints.items():
        success = test_meditation_api(plan_type_name, api_url)
        results[plan_type_name] = success
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for plan_type_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{plan_type_name}: {status}")

if __name__ == "__main__":
    main() 