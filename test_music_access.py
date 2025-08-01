#!/usr/bin/env python3
"""
Test script to verify music file access and URL generation
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.services import ExternalMeditationService
from apps.accounts.models import CustomUser, RitualType, Rituals, MeditationGenerate
from django.core.files.base import ContentFile
import os

def test_music_file_access():
    """Test music file access and URL generation"""
    
    print("Testing music file access...")
    
    # Check if placeholder MP3 exists
    placeholder_path = os.path.join(os.path.dirname(__file__), 'apps', 'accounts', 'muzic', 'sleep_manifestation.mp3')
    print(f"Placeholder MP3 path: {placeholder_path}")
    print(f"Placeholder MP3 exists: {os.path.exists(placeholder_path)}")
    
    if os.path.exists(placeholder_path):
        print(f"Placeholder MP3 size: {os.path.getsize(placeholder_path)} bytes")
    
    # Test file URL generation
    service = ExternalMeditationService()
    
    # Create a test meditation record
    try:
        user = CustomUser.objects.first()
        if not user:
            print("No users found, creating test user...")
            user = CustomUser.objects.create(
                username='test_user',
                email='test@example.com'
            )
        
        # Create ritual type if it doesn't exist
        ritual_type, created = RitualType.objects.get_or_create(
            name="Morning Spark",
            defaults={"description": "Test ritual type"}
        )
        
        # Create ritual
        ritual = Rituals.objects.create(
            name="Test Meditation",
            description="Test meditation",
            ritual_type="story",
            tone="dreamy",
            voice="female",
            duration="2"
        )
        
        # Create test file content
        test_content = b"Test audio content"
        file_content = ContentFile(test_content, name="test_meditation.mp3")
        
        # Create meditation record
        meditation = MeditationGenerate.objects.create(
            user=user,
            details=ritual,
            ritual_type=ritual_type,
            file=file_content
        )
        
        print(f"Created meditation record: {meditation.id}")
        print(f"File path: {meditation.file.path if meditation.file else 'No file'}")
        print(f"File URL: {meditation.file.url if meditation.file else 'No file'}")
        
        # Test URL generation
        file_url = service._get_file_url(meditation)
        print(f"Generated file URL: {file_url}")
        
        # Test placeholder file creation
        placeholder_content = service.create_placeholder_file("test_placeholder.mp3")
        print(f"Placeholder file created: {placeholder_content.name}")
        print(f"Placeholder file size: {len(placeholder_content.read())} bytes")
        
        print("✅ Music file access test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in music file access test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_music_file_access() 