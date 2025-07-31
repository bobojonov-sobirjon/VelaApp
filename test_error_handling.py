#!/usr/bin/env python
"""
Test script to verify error handling in CombinedProfileSerializer
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.serializers import CombinedProfileSerializer
from apps.accounts.models import CustomUser, RitualType
from rest_framework.test import APIRequestFactory
from rest_framework import status
from config.exceptions import (
    PlanTypeNotFoundError, AuthenticationRequiredError, 
    SubscriptionRequiredError, TrialExpiredError, 
    MeditationGenerationError
)

def test_error_handling():
    """Test various error scenarios"""
    
    factory = APIRequestFactory()
    
    # Test 1: Missing plan_type (should return 400)
    print("Test 1: Missing plan_type")
    try:
        serializer = CombinedProfileSerializer(data={})
        serializer.is_valid(raise_exception=True)
    except Exception as e:
        print(f"Expected error: {type(e).__name__} - {e}")
    
    # Test 2: Invalid plan_type ID (should return 404)
    print("\nTest 2: Invalid plan_type ID")
    try:
        serializer = CombinedProfileSerializer(data={'plan_type': 99999})
        serializer.is_valid(raise_exception=True)
    except PlanTypeNotFoundError as e:
        print(f"Expected error: {type(e).__name__} - {e}")
        print(f"Status code: {e.status_code}")
    
    # Test 3: Unknown plan type name (should return 404)
    print("\nTest 3: Unknown plan type name")
    try:
        # Create a plan type with unknown name
        plan_type = RitualType.objects.create(name="Unknown Plan")
        serializer = CombinedProfileSerializer(data={'plan_type': plan_type.id})
        serializer.is_valid(raise_exception=True)
        
        # This should fail in generate_meditation method
        request = factory.post('/')
        serializer.context = {'request': request}
        serializer.create(serializer.validated_data)
        
    except PlanTypeNotFoundError as e:
        print(f"Expected error: {type(e).__name__} - {e}")
        print(f"Status code: {e.status_code}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
    
    # Test 4: Authentication required (should return 401)
    print("\nTest 4: Authentication required")
    try:
        serializer = CombinedProfileSerializer(data={'plan_type': 1})
        serializer.is_valid(raise_exception=True)
        
        # Create request without user
        request = factory.post('/')
        request.user = None  # No authenticated user
        serializer.context = {'request': request}
        serializer.create(serializer.validated_data)
        
    except AuthenticationRequiredError as e:
        print(f"Expected error: {type(e).__name__} - {e}")
        print(f"Status code: {e.status_code}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_error_handling() 