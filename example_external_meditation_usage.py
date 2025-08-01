#!/usr/bin/env python3
"""
Example script to demonstrate the updated External Meditation API usage
This script shows how to use the new key-based request format
"""

import requests
import json
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your Django server URL
RITUAL_TYPES_ENDPOINT = f"{BASE_URL}/api/ritual-types/"
EXTERNAL_MEDITATION_ENDPOINT = f"{BASE_URL}/api/meditation/external/"

def create_ritual_types_if_needed():
    """Create ritual types if they don't exist"""
    print("🔧 Setting up ritual types...")
    
    ritual_types_data = [
        {"name": "Sleep Manifestation"},
        {"name": "Morning Spark"},
        {"name": "Calming Reset"},
        {"name": "Dream Visualizer"}
    ]
    
    for ritual_data in ritual_types_data:
        try:
            response = requests.post(
                f"{BASE_URL}/api/ritual-types/",
                json=ritual_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 201:
                print(f"   ✅ Created: {ritual_data['name']}")
            elif response.status_code == 400:
                print(f"   ⚠️  Already exists: {ritual_data['name']}")
            else:
                print(f"   ❌ Failed to create {ritual_data['name']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error creating {ritual_data['name']}: {str(e)}")

def get_ritual_types():
    """Get available ritual types"""
    try:
        response = requests.get(RITUAL_TYPES_ENDPOINT, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get ritual types: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting ritual types: {str(e)}")
        return []

def test_external_meditation_api():
    print("\n🧘 Testing External Meditation API (New Key-Based Format)")
    print("=" * 60)
    
    create_ritual_types_if_needed()
    ritual_types = get_ritual_types()
    if not ritual_types:
        print("❌ No ritual types available. Please create some first.")
        return
    
    # New test cases with key-based format
    test_cases = [
        {
            "name": "Sleep Manifestation Test",
            "plan_type_id": ritual_types[0]['id'],  # Sleep Manifestation
            "data": {
                "name": "John Doe",
                "goals": "I want to achieve deep, restful sleep every night",
                "dreamlife": "I dream of a peaceful, stress-free life with abundant energy",
                "dream_activities": "Reading, meditation, and spending time in nature",
                "ritual_type": "story",  # Key instead of "Story"
                "tone": "dreamy",        # Key instead of "Dreamy"
                "voice": "female",       # Key instead of "Female"
                "length": "5",           # Key instead of 5
                "check_in": "Feeling ready for a peaceful night"
            }
        },
        {
            "name": "Morning Spark Test",
            "plan_type_id": ritual_types[1]['id'],  # Morning Spark
            "data": {
                "name": "Jane Smith",
                "goals": "I want to start each day with energy and motivation",
                "dreamlife": "I dream of a productive, successful career with work-life balance",
                "dream_activities": "Exercise, healthy eating, and personal development",
                "ritual_type": "guided_meditations",  # Key instead of "Guided meditations"
                "tone": "asmr",                       # Key instead of "ASMR"
                "voice": "male",                      # Key instead of "Male"
                "length": "2",                        # Key instead of 2
                "check_in": "Ready to seize the day"
            }
        },
        {
            "name": "Calming Reset Test",
            "plan_type_id": ritual_types[2]['id'],  # Calming Reset
            "data": {
                "name": "Mike Johnson",
                "goals": "I want to find inner peace and reduce stress",
                "dreamlife": "I dream of a calm, balanced life with emotional stability",
                "dream_activities": "Yoga, nature walks, and mindfulness practices",
                "ritual_type": "story",      # Key instead of "Story"
                "tone": "dreamy",            # Key instead of "Dreamy"
                "voice": "female",           # Key instead of "Female"
                "length": "10",              # Key instead of 10
                "check_in": "Seeking tranquility"
            }
        },
        {
            "name": "Dream Visualizer Test",
            "plan_type_id": ritual_types[3]['id'],  # Dream Visualizer
            "data": {
                "name": "Sarah Wilson",
                "goals": "I want to manifest my dreams into reality",
                "dreamlife": "I dream of achieving all my life goals and aspirations",
                "dream_activities": "Visualization, goal setting, and positive affirmations",
                "ritual_type": "guided_meditations",  # Key instead of "Guided meditations"
                "tone": "asmr",                       # Key instead of "ASMR"
                "voice": "male",                      # Key instead of "Male"
                "length": "5",                        # Key instead of 5
                "check_in": "Visualizing success"
            }
        }
    ]
    
    print("\n📋 Available Keys for Choice Fields:")
    print("   ritual_type: 'story', 'guided_meditations'")
    print("   tone: 'dreamy', 'asmr'")
    print("   voice: 'male', 'female'")
    print("   length: '2', '5', '10'")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Plan Type ID: {test_case['plan_type_id']}")
        print(f"   API Endpoint: {EXTERNAL_MEDITATION_ENDPOINT}")
        
        request_data = test_case['data'].copy()
        request_data['plan_type'] = test_case['plan_type_id']
        
        print(f"\n   📤 Request Data (New Key-Based Format):")
        print(f"   {json.dumps(request_data, indent=6)}")
        
        try:
            response = requests.post(
                EXTERNAL_MEDITATION_ENDPOINT,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"\n   📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Message: {result.get('message', 'N/A')}")
                print(f"   Plan Type: {result.get('plan_type', 'N/A')}")
                print(f"   Endpoint Used: {result.get('endpoint_used', 'N/A')}")
                print(f"   File URL: {result.get('file_url', 'N/A')}")
                print(f"   Meditation ID: {result.get('meditation_id', 'N/A')}")
                if 'api_response' in result:
                    print(f"   API Response: {json.dumps(result['api_response'], indent=2)}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error Text: {response.text}")
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Request took too long")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error: Could not connect to server")
        except Exception as e:
            print(f"   💥 Unexpected Error: {str(e)}")
        
        print("-" * 60)

def test_invalid_keys():
    print("\n🚫 Testing Invalid Key Validation")
    print("=" * 40)
    
    invalid_test_cases = [
        {
            "name": "Invalid Ritual Type Key",
            "data": {
                "name": "Test User",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": 1,
                "ritual_type": "invalid_key",  # Invalid key
                "tone": "dreamy",
                "voice": "female",
                "length": "5",
                "check_in": "Test check in"
            }
        },
        {
            "name": "Invalid Tone Key",
            "data": {
                "name": "Test User",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": 1,
                "ritual_type": "story",
                "tone": "invalid_tone",  # Invalid key
                "voice": "female",
                "length": "5",
                "check_in": "Test check in"
            }
        },
        {
            "name": "Invalid Voice Key",
            "data": {
                "name": "Test User",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": 1,
                "ritual_type": "story",
                "tone": "dreamy",
                "voice": "invalid_voice",  # Invalid key
                "length": "5",
                "check_in": "Test check in"
            }
        },
        {
            "name": "Invalid Length Key",
            "data": {
                "name": "Test User",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": 1,
                "ritual_type": "story",
                "tone": "dreamy",
                "voice": "female",
                "length": "15",  # Invalid key
                "check_in": "Test check in"
            }
        }
    ]
    
    for i, test_case in enumerate(invalid_test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        try:
            response = requests.post(
                EXTERNAL_MEDITATION_ENDPOINT,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"   ✅ Validation Error (Expected): {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   ✅ Validation Error (Expected): {response.text}")
            else:
                print(f"   ❌ Unexpected Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        print("-" * 40)

def main():
    print("🚀 External Meditation API Testing Script")
    print("=" * 50)
    print("This script demonstrates the new key-based request format")
    print("Instead of sending values like 'Story', 'Dreamy', 'Female', 5")
    print("Now send keys like 'story', 'dreamy', 'female', '5'")
    print("=" * 50)
    
    # Test valid requests
    test_external_meditation_api()
    
    # Test invalid keys
    test_invalid_keys()
    
    print("\n✅ Testing Complete!")
    print("\n📝 Summary:")
    print("   - Valid keys for ritual_type: 'story', 'guided_meditations'")
    print("   - Valid keys for tone: 'dreamy', 'asmr'")
    print("   - Valid keys for voice: 'male', 'female'")
    print("   - Valid keys for length: '2', '5', '10'")
    print("   - plan_type should be a valid RitualType ID")
    print("\nUpdate BASE_URL if your server is running on a different host/port")

if __name__ == "__main__":
    main() 