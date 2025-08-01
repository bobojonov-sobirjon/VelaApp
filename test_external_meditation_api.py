#!/usr/bin/env python3
"""
Test script for the External Meditation API
This script demonstrates how to use the new external meditation API endpoint.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"  # Change this to your Django server URL
API_ENDPOINT = f"{BASE_URL}/api/meditation/external/"

# Test data for different plan types
test_cases = [
    {
        "name": "Sleep Manifestation Test",
        "plan_type": "Sleep Manifestation",
        "data": {
            "name": "John Doe",
            "goals": "I want to achieve deep, restful sleep every night",
            "dreamlife": "I dream of a peaceful, stress-free life with abundant energy",
            "dream_activities": "Reading, meditation, and spending time in nature",
            "ritual_type": "Story",
            "tone": "Dreamy",
            "voice": "Female",
            "length": 5,
            "check_in": "Feeling ready for a peaceful night"
        }
    },
    {
        "name": "Morning Spark Test",
        "plan_type": "Morning Spark",
        "data": {
            "name": "Jane Smith",
            "goals": "I want to start each day with energy and motivation",
            "dreamlife": "I dream of a successful career and fulfilling relationships",
            "dream_activities": "Exercise, healthy eating, and personal growth",
            "ritual_type": "Guided",
            "tone": "ASMR",
            "voice": "Male",
            "length": 2,
            "check_in": "Ready to seize the day"
        }
    },
    {
        "name": "Calming Reset Test",
        "plan_type": "Calming Reset",
        "data": {
            "name": "Mike Johnson",
            "goals": "I want to find inner peace and reduce stress",
            "dreamlife": "I dream of a balanced life with harmony and tranquility",
            "dream_activities": "Yoga, meditation, and creative pursuits",
            "ritual_type": "Story",
            "tone": "Dreamy",
            "voice": "Female",
            "length": 10,
            "check_in": "Seeking calm and clarity"
        }
    },
    {
        "name": "Dream Visualizer Test",
        "plan_type": "Dream Visualizer",
        "data": {
            "name": "Sarah Wilson",
            "goals": "I want to manifest my dreams and achieve my highest potential",
            "dreamlife": "I dream of living my purpose and making a positive impact",
            "dream_activities": "Visualization, goal setting, and inspired action",
            "ritual_type": "Guided",
            "tone": "ASMR",
            "voice": "Male",
            "length": 5,
            "check_in": "Aligned with my highest vision"
        }
    }
]

def test_external_meditation_api():
    """
    Test the external meditation API with different plan types
    """
    print("🧘 Testing External Meditation API")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Plan Type: {test_case['plan_type']}")
        print(f"   API Endpoint: {API_ENDPOINT}")
        
        # Prepare the request data
        request_data = test_case['data'].copy()
        request_data['plan_type'] = test_case['plan_type']
        
        try:
            # Make the API request
            print(f"   Sending request...")
            response = requests.post(
                API_ENDPOINT,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Print response
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Message: {result.get('message', 'N/A')}")
                print(f"   Endpoint Used: {result.get('endpoint_used', 'N/A')}")
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
        
        print("-" * 50)

def test_validation_errors():
    """
    Test validation errors with invalid data
    """
    print("\n🔍 Testing Validation Errors")
    print("=" * 50)
    
    invalid_test_cases = [
        {
            "name": "Missing Required Fields",
            "data": {
                "name": "John",
                "goals": "Test goals"
                # Missing dreamlife, dream_activities, plan_type
            }
        },
        {
            "name": "Invalid Plan Type",
            "data": {
                "name": "John",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": "Invalid Plan Type"
            }
        },
        {
            "name": "Invalid Length",
            "data": {
                "name": "John",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": "Sleep Manifestation",
                "length": 15  # Invalid length
            }
        }
    ]
    
    for i, test_case in enumerate(invalid_test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        try:
            response = requests.post(
                API_ENDPOINT,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                result = response.json()
                print(f"   ✅ Validation Error (Expected)")
                print(f"   Error: {result.get('error', 'N/A')}")
                if 'details' in result:
                    print(f"   Details: {json.dumps(result['details'], indent=2)}")
            else:
                print(f"   ❌ Unexpected Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("🚀 External Meditation API Test Suite")
    print("This script tests the new external meditation API endpoint.")
    print("Make sure your Django server is running on localhost:8000")
    print("Update BASE_URL if your server is running on a different host/port")
    print()
    
    # Test valid requests
    test_external_meditation_api()
    
    # Test validation errors
    test_validation_errors()
    
    print("\n✨ Test completed!")
    print("Check the output above to see the results of each test case.") 