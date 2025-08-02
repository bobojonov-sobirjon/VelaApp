#!/usr/bin/env python3
"""
Setup script for RitualType records
Creates the required ritual types for external meditation API testing
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import RitualType

def setup_ritual_types():
    """Create the required ritual types for external meditation API"""
    
    # Define the ritual types that map to external APIs
    ritual_types = [
        {
            'name': 'Sleep Manifestation',
            'description': 'External API for sleep manifestation meditations'
        },
        {
            'name': 'Morning Spark', 
            'description': 'External API for morning spark meditations'
        },
        {
            'name': 'Calming Reset',
            'description': 'External API for calming reset meditations'
        },
        {
            'name': 'Dream Visualizer',
            'description': 'External API for dream visualizer meditations'
        }
    ]
    
    print("Setting up RitualType records...")
    
    for ritual_type_data in ritual_types:
        ritual_type, created = RitualType.objects.get_or_create(
            name=ritual_type_data['name'],
            defaults={'description': ritual_type_data['description']}
        )
        
        if created:
            print(f"✅ Created: {ritual_type.name} (ID: {ritual_type.id})")
        else:
            print(f"ℹ️ Already exists: {ritual_type.name} (ID: {ritual_type.id})")
    
    print("\nAll ritual types are ready!")
    print("\nAvailable RitualType records:")
    for rt in RitualType.objects.all():
        print(f"  ID: {rt.id}, Name: {rt.name}")

if __name__ == '__main__':
    setup_ritual_types() 