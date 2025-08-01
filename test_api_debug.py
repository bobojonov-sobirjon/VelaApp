#!/usr/bin/env python3
"""
Debug script for External Meditation API
"""

import requests
import json
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import RitualType

# Test data
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

print("🧪 Testing External Meditation API Debug")
print("=" * 50)

# Check if ritual type exists
try:
    ritual_type = RitualType.objects.get(id=2)
    print(f"✅ Found ritual type: {ritual_type.name} (ID: 2)")
except RitualType.DoesNotExist:
    print("❌ Ritual type with ID 2 does not exist")
    # List all available ritual types
    ritual_types = RitualType.objects.all()
    print("Available ritual types:")
    for rt in ritual_types:
        print(f"  - ID: {rt.id}, Name: {rt.name}")
    sys.exit(1)

# Test the API endpoint
api_url = "http://localhost:8000/api/auth/meditation/external/"

print(f"\n📤 Sending request to: {api_url}")
print(f"📋 Request data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        api_url,
        json=test_data,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error Text: {response.text}")
            
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Could not connect to server")
    print("Make sure the Django server is running on localhost:8000")
except requests.exceptions.Timeout:
    print("❌ Timeout: Request took too long")
except Exception as e:
    print(f"❌ Unexpected Error: {str(e)}")

print("\n✅ Debug test complete!") 