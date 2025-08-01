#!/usr/bin/env python3
"""
Test script for the Meditation Detail API endpoint
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8080"  # Change this to your server URL
API_ENDPOINT = f"{BASE_URL}/api/auth/meditation/"

def test_get_meditation_by_id(meditation_id, auth_token):
    """Test getting a meditation by ID"""
    
    print(f"🧪 Testing Get Meditation by ID: {meditation_id}")
    print("=" * 50)
    
    # Print the request details
    print(f"📤 Request URL: {API_ENDPOINT}{meditation_id}/")
    print(f"📤 Method: GET")
    print(f"📤 Authorization: Bearer {auth_token[:20]}...")
    print()
    
    try:
        # Make the API request
        response = requests.get(
            f"{API_ENDPOINT}{meditation_id}/",
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
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
            
            # Display key information
            print("\n📋 Key Information:")
            print(f"   • Meditation ID: {response_data.get('id')}")
            print(f"   • Created At: {response_data.get('created_at')}")
            print(f"   • File URL: {response_data.get('file')}")
            
            if response_data.get('details'):
                details = response_data['details']
                print(f"   • Ritual Name: {details.get('name')}")
                print(f"   • Ritual Type: {details.get('ritual_type')}")
                print(f"   • Tone: {details.get('tone')}")
                print(f"   • Voice: {details.get('voice')}")
                print(f"   • Duration: {details.get('duration')}")
            
            if response_data.get('ritual_type'):
                ritual_type = response_data['ritual_type']
                print(f"   • Plan Type: {ritual_type.get('name')}")
                
        elif response.status_code == 404:
            print("❌ Meditation not found!")
            print(f"📥 Error Response:")
            print(response.text)
        elif response.status_code == 401:
            print("❌ Unauthorized - Check your authentication token!")
            print(f"📥 Error Response:")
            print(response.text)
        else:
            print("❌ Unexpected error!")
            print(f"📥 Error Response:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

def test_get_nonexistent_meditation(auth_token):
    """Test getting a meditation that doesn't exist"""
    
    print("\n🧪 Testing Get Non-existent Meditation")
    print("=" * 50)
    
    # Use a very high ID that likely doesn't exist
    nonexistent_id = 999999
    
    print(f"📤 Request URL: {API_ENDPOINT}{nonexistent_id}/")
    print(f"📤 Method: GET")
    print()
    
    try:
        response = requests.get(
            f"{API_ENDPOINT}{nonexistent_id}/",
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent meditation!")
            print(f"📥 Error Response:")
            print(response.text)
        else:
            print("❌ Expected 404 but got different status!")
            print(f"📥 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

def test_unauthorized_access():
    """Test accessing without authentication"""
    
    print("\n🧪 Testing Unauthorized Access")
    print("=" * 50)
    
    meditation_id = 1
    
    print(f"📤 Request URL: {API_ENDPOINT}{meditation_id}/")
    print(f"📤 Method: GET")
    print(f"📤 No Authorization header")
    print()
    
    try:
        response = requests.get(
            f"{API_ENDPOINT}{meditation_id}/",
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly returned 401 for unauthorized access!")
            print(f"📥 Error Response:")
            print(response.text)
        else:
            print("❌ Expected 401 but got different status!")
            print(f"📥 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Meditation Detail API Tests")
    print("=" * 50)
    
    # Replace with your actual authentication token
    AUTH_TOKEN = "YOUR_JWT_TOKEN_HERE"
    
    # Replace with an actual meditation ID from your database
    MEDITATION_ID = 1
    
    if AUTH_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("⚠️  Please update the AUTH_TOKEN variable with your actual JWT token")
        print("⚠️  Please update the MEDITATION_ID variable with an actual meditation ID")
        print("\n📝 Example usage:")
        print("   AUTH_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'")
        print("   MEDITATION_ID = 123")
        print("\n🔗 API Endpoint:")
        print(f"   GET {API_ENDPOINT}{MEDITATION_ID}/")
        print("\n📋 Required Headers:")
        print("   Authorization: Bearer YOUR_JWT_TOKEN")
        print("   Content-Type: application/json")
    else:
        # Test valid meditation retrieval
        test_get_meditation_by_id(MEDITATION_ID, AUTH_TOKEN)
        
        # Test non-existent meditation
        test_get_nonexistent_meditation(AUTH_TOKEN)
        
        # Test unauthorized access
        test_unauthorized_access()
    
    print("\n✅ Tests completed!") 