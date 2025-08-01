#!/usr/bin/env python3
"""
Example script demonstrating how to use the updated ExternalMeditationAPIView
This script shows how to:
1. Get available ritual types (plan types)
2. Use plan_type ID instead of string names
3. Handle the response with file URL and meditation ID
"""

import requests
import json
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import RitualType

# API endpoints
BASE_URL = "http://localhost:8000"  # Change this to your Django server URL
RITUAL_TYPES_ENDPOINT = f"{BASE_URL}/api/ritual-types/"
EXTERNAL_MEDITATION_ENDPOINT = f"{BASE_URL}/api/meditation/external/"

def get_ritual_types():
    """
    Get available ritual types and their IDs
    """
    print("🔍 Getting available ritual types...")
    
    try:
        response = requests.get(RITUAL_TYPES_ENDPOINT)
        
        if response.status_code == 200:
            ritual_types = response.json()
            print("✅ Available ritual types:")
            for ritual_type in ritual_types:
                print(f"   ID: {ritual_type['id']}, Name: {ritual_type['name']}")
            return ritual_types
        else:
            print(f"❌ Error getting ritual types: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return []

def create_ritual_types_if_needed():
    """
    Create ritual types if they don't exist
    """
    ritual_types = [
        {"name": "Sleep Manifestation", "description": "For deep, restful sleep"},
        {"name": "Morning Spark", "description": "For energy and motivation"},
        {"name": "Calming Reset", "description": "For inner peace and stress reduction"},
        {"name": "Dream Visualizer", "description": "For manifesting dreams and potential"}
    ]
    
    for ritual_type_data in ritual_types:
        ritual_type, created = RitualType.objects.get_or_create(
            name=ritual_type_data["name"],
            defaults={"description": ritual_type_data["description"]}
        )
        if created:
            print(f"✅ Created ritual type: {ritual_type.name} (ID: {ritual_type.id})")
        else:
            print(f"📋 Found existing ritual type: {ritual_type.name} (ID: {ritual_type.id})")

def test_external_meditation_api():
    """
    Test the external meditation API with different plan types
    """
    print("\n🧘 Testing External Meditation API")
    print("=" * 50)
    
    # Create ritual types if needed
    create_ritual_types_if_needed()
    
    # Get ritual types
    ritual_types = get_ritual_types()
    if not ritual_types:
        print("❌ No ritual types available. Please create some first.")
        return
    
    # Test cases with different plan type IDs
    test_cases = [
        {
            "name": "Sleep Manifestation Test",
            "plan_type_id": ritual_types[0]['id'],  # Sleep Manifestation
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
            "plan_type_id": ritual_types[1]['id'],  # Morning Spark
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
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Plan Type ID: {test_case['plan_type_id']}")
        print(f"   API Endpoint: {EXTERNAL_MEDITATION_ENDPOINT}")
        
        # Prepare the request data
        request_data = test_case['data'].copy()
        request_data['plan_type'] = test_case['plan_type_id']
        
        try:
            # Make the API request
            print(f"   Sending request...")
            response = requests.post(
                EXTERNAL_MEDITATION_ENDPOINT,
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
            "name": "Invalid Plan Type ID",
            "data": {
                "name": "John",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": 99999  # Invalid ID
            }
        },
        {
            "name": "Invalid Length",
            "data": {
                "name": "John",
                "goals": "Test goals",
                "dreamlife": "Test dream life",
                "dream_activities": "Test activities",
                "plan_type": 1,  # Valid ID
                "length": 15  # Invalid length
            }
        }
    ]
    
    for i, test_case in enumerate(invalid_test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   API Endpoint: {EXTERNAL_MEDITATION_ENDPOINT}")
        
        try:
            print(f"   Sending request...")
            response = requests.post(
                EXTERNAL_MEDITATION_ENDPOINT,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                print(f"   ✅ Expected validation error received!")
                try:
                    error_data = response.json()
                    print(f"   Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error Text: {response.text}")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                try:
                    result = response.json()
                    print(f"   Response: {json.dumps(result, indent=2)}")
                except:
                    print(f"   Response Text: {response.text}")
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Request took too long")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error: Could not connect to server")
        except Exception as e:
            print(f"   💥 Unexpected Error: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("🚀 External Meditation API Example")
    print("=" * 50)
    print("This script demonstrates the updated ExternalMeditationAPIView")
    print("Key changes:")
    print("- plan_type now accepts RitualType ID instead of string names")
    print("- Response includes file_url and meditation_id")
    print("- Files are automatically saved to the database")
    print("=" * 50)
    
    # Test the API
    test_external_meditation_api()
    
    # Test validation errors
    test_validation_errors()
    
    print("\n✨ Example completed!")
    print("Check the output above to see the results of each test case.")
    print("\n📝 Key Features:")
    print("- plan_type field now accepts RitualType IDs")
    print("- Files are automatically saved and URLs are returned")
    print("- Meditation records are created in the database")
    print("- Error handling includes file creation with placeholders") 