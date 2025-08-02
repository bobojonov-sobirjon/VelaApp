import requests
import json
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from datetime import datetime
import os
from django.utils import timezone

from apps.accounts.models import RitualType, Rituals, MeditationGenerate

logger = logging.getLogger(__name__)


class GoogleLoginService:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self):
        """Generate Google OAuth2 authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    def exchange_code_for_tokens(self, code):
        """Exchange authorization code for access and refresh tokens"""
        try:
            response = requests.post(self.token_url, data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            })
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in')
                }
            else:
                logger.error(f"Google token exchange failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error exchanging Google code for tokens: {str(e)}")
            return None

    def get_user_info(self, access_token):
        """Get user information from Google"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.userinfo_url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get Google user info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Google user info: {str(e)}")
            return None


class FacebookLoginService:
    def __init__(self):
        self.client_id = settings.FACEBOOK_CLIENT_ID
        self.client_secret = settings.FACEBOOK_CLIENT_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
        self.auth_url = "https://www.facebook.com/v18.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        self.userinfo_url = "https://graph.facebook.com/v18.0/me"

    def get_authorization_url(self):
        """Generate Facebook OAuth2 authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'email public_profile',
            'response_type': 'code'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    def exchange_code_for_tokens(self, code):
        """Exchange authorization code for access token"""
        try:
            response = requests.get(self.token_url, params={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            })
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'access_token': token_data.get('access_token'),
                    'expires_in': token_data.get('expires_in')
                }
            else:
                logger.error(f"Facebook token exchange failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error exchanging Facebook code for tokens: {str(e)}")
            return None

    def get_user_info(self, access_token):
        """Get user information from Facebook"""
        try:
            params = {
                'fields': 'id,name,email,first_name,last_name',
                'access_token': access_token
            }
            response = requests.get(self.userinfo_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get Facebook user info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Facebook user info: {str(e)}")
            return None


class ExternalMeditationService:
    """
    Service for handling external meditation API requests
    
    Maps plan_type IDs to external API endpoints and transforms request data
    to match the external API format. Saves returned MP3 files to MeditationGenerate model.
    """
    
    def __init__(self):
        # External API endpoints mapping based on ritual type names
        self.api_endpoints = {
            "Sleep Manifestation": "http://31.97.98.47:8000/sleep",
            "Morning Spark": "http://31.97.98.47:8000/spark", 
            "Calming Reset": "http://31.97.98.47:8000/calm",
            "Dream Visualizer": "http://31.97.98.47:8000/dream"
        }
        
        # Field mappings from our format to external API format
        self.field_mappings = {
            'duration': 'length',
            'ritual_type': 'ritual_type',
            'voice': 'voice',
            'tone': 'tone',
            'goals': 'goals',
            'dream': 'dreamlife',
            'happiness': 'dream_activities',
            'age_range': 'name',  # Using age_range as name for external API
            'gender': 'name'  # Using gender as name for external API
        }
    
    def process_meditation_request(self, user, validated_data):
        """
        Process meditation request and send to appropriate external API
        
        Args:
            user: The authenticated user
            validated_data: Validated data from ExternalMeditationSerializer
            
        Returns:
            dict: Response with success status, message, and file details
        """
        print(f"🔍 Starting ExternalMeditationService.process_meditation_request")
        print(f"📝 Validated data: {validated_data}")
        
        try:
            # Get plan type from validated data
            plan_type_id = validated_data.get('plan_type')
            print(f"🎯 Plan type ID: {plan_type_id}")
            
            # Get the ritual type name from the plan_type ID
            try:
                ritual_type = RitualType.objects.get(id=plan_type_id)
                ritual_type_name = ritual_type.name
                print(f"✅ Found ritual type: {ritual_type_name}")
            except RitualType.DoesNotExist:
                print(f"❌ RitualType with ID {plan_type_id} does not exist")
                return {
                    "success": False,
                    "message": f"Plan type with ID {plan_type_id} does not exist",
                    "plan_type": f"ID: {plan_type_id}",
                    "ritual_type_name": None
                }
            
            # Get the appropriate API endpoint based on ritual type name
            api_endpoint = self._get_api_endpoint(ritual_type_name)
            print(f"🌐 API endpoint: {api_endpoint}")
            
            if not api_endpoint:
                print(f"❌ No API endpoint found for ritual type: {ritual_type_name}")
                return {
                    "success": False,
                    "message": f"No API endpoint found for ritual type: {ritual_type_name}",
                    "plan_type": ritual_type_name,
                    "ritual_type_name": ritual_type_name
                }
            
            # Transform data for external API
            external_api_data = self._transform_data_for_external_api(validated_data)
            print(f"🔄 Transformed data for external API: {external_api_data}")
            
            # Make request to external API
            print(f"📡 Making request to external API...")
            api_response = self._make_external_api_request(api_endpoint, external_api_data)
            print(f"📥 External API response: {api_response}")
            
            if not api_response.get('success'):
                print(f"❌ External API request failed: {api_response.get('error', 'Unknown error')}")
                
                # Check if it's a timeout or connection error - create meditation record anyway
                if 'timeout' in api_response.get('error', '').lower() or 'connection' in api_response.get('error', '').lower():
                    print(f"⚠️ External API unavailable, creating meditation record without file...")
                    
                    # Save the meditation file and create MeditationGenerate record without file
                    meditation_record = self._save_meditation_file(
                        user=user,
                        ritual_type_name=ritual_type_name,
                        file_data=None,
                        file_name=None
                    )
                    
                    return {
                        "success": True,
                        "message": "Meditation record created (external API unavailable)",
                        "plan_type": ritual_type_name,
                        "endpoint_used": api_endpoint,
                        "api_response": api_response,
                        "file_url": None,
                        "meditation_id": meditation_record.id,
                        "ritual_type_name": ritual_type_name,
                        "warning": "External API was unavailable, meditation created without audio file"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"External API request failed: {api_response.get('error', 'Unknown error')}",
                        "plan_type": ritual_type_name,
                        "endpoint_used": api_endpoint,
                        "api_response": api_response,
                        "ritual_type_name": ritual_type_name
                    }
            
            # Save the meditation file and create MeditationGenerate record
            print(f"💾 Saving meditation file...")
            meditation_record = self._save_meditation_file(
                user=user,
                ritual_type_name=ritual_type_name,
                file_data=api_response.get('file_data'),
                file_name=api_response.get('file_name', 'meditation.mp3')
            )
            print(f"✅ Meditation record created with ID: {meditation_record.id}")
            
            return {
                "success": True,
                "message": "Meditation generated successfully",
                "plan_type": ritual_type_name,
                "endpoint_used": api_endpoint,
                "api_response": api_response,
                "file_url": meditation_record.file.url if meditation_record.file else None,
                "meditation_id": meditation_record.id,
                "ritual_type_name": ritual_type_name
            }
            
        except Exception as e:
            print(f"💥 Exception in ExternalMeditationService.process_meditation_request: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error in ExternalMeditationService.process_meditation_request: {str(e)}")
            return {
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "plan_type": validated_data.get('plan_type', 'Unknown'),
                "ritual_type_name": None
            }
    
    def _get_api_endpoint(self, ritual_type_name):
        """
        Get the appropriate API endpoint based on ritual type name
        
        Args:
            ritual_type_name: Name of the ritual type
            
        Returns:
            str: API endpoint URL or None if not found
        """
        return self.api_endpoints.get(ritual_type_name)
    
    def _transform_data_for_external_api(self, validated_data):
        """
        Transform our data format to match external API requirements
        
        Args:
            validated_data: Validated data from serializer
            
        Returns:
            dict: Data formatted for external API
        """
        print(f"🔄 Starting data transformation...")
        external_data = {}
        
        # Map fields according to the mapping dictionary
        for our_field, external_field in self.field_mappings.items():
            if our_field in validated_data:
                external_data[external_field] = validated_data[our_field]
                print(f"  📝 Mapped {our_field} -> {external_field}: {validated_data[our_field]}")
        
        # Handle special transformations for external API format
        if 'ritual_type' in external_data:
            # Convert to proper case for external API
            original_value = external_data['ritual_type']
            if external_data['ritual_type'] == 'story':
                external_data['ritual_type'] = 'Story'
            elif external_data['ritual_type'] == 'guided_meditations':
                external_data['ritual_type'] = 'Guided'
            print(f"  🔄 ritual_type: {original_value} -> {external_data['ritual_type']}")
        
        if 'tone' in external_data:
            # Convert to proper case for external API
            original_value = external_data['tone']
            if external_data['tone'] == 'dreamy':
                external_data['tone'] = 'Dreamy'
            elif external_data['tone'] == 'asmr':
                external_data['tone'] = 'ASMR'
            print(f"  🔄 tone: {original_value} -> {external_data['tone']}")
        
        if 'voice' in external_data:
            # Convert to proper case for external API
            original_value = external_data['voice']
            if external_data['voice'] == 'female':
                external_data['voice'] = 'Female'
            elif external_data['voice'] == 'male':
                external_data['voice'] = 'Male'
            print(f"  🔄 voice: {original_value} -> {external_data['voice']}")
        
        if 'length' in external_data:
            # Convert to integer for external API
            original_value = external_data['length']
            try:
                external_data['length'] = int(external_data['length'])
            except (ValueError, TypeError):
                external_data['length'] = 2  # Default to 2 minutes
            print(f"  🔄 length: {original_value} -> {external_data['length']}")
        
        print(f"✅ Final transformed data: {external_data}")
        return external_data
    
    def _make_external_api_request(self, api_endpoint, data):
        """
        Make HTTP request to external API
        
        Args:
            api_endpoint: The API endpoint URL
            data: Data to send to the API
            
        Returns:
            dict: Response from external API
        """
        try:
            print(f"📡 Making request to external API: {api_endpoint}")
            print(f"📤 Request data: {data}")
            logger.info(f"Making request to external API: {api_endpoint}")
            logger.info(f"Request data: {data}")
            
            response = requests.post(
                api_endpoint,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10  # 10 second timeout for faster testing
            )
            
            print(f"📥 Response status: {response.status_code}")
            logger.info(f"External API response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Success response: {response_data}")
                logger.info(f"External API response: {response_data}")
                
                # Check if the response contains file data
                if 'file' in response_data or 'file_url' in response_data:
                    file_url = response_data.get('file_url') or response_data.get('file')
                    print(f"📁 File URL found: {file_url}")
                    return {
                        'success': True,
                        'file_data': file_url,
                        'file_name': f"meditation_{int(timezone.now().timestamp())}.mp3",
                        'response_data': response_data
                    }
                else:
                    print(f"⚠️ No file URL in response")
                    return {
                        'success': True,
                        'file_data': None,
                        'file_name': f"meditation_{int(timezone.now().timestamp())}.mp3",
                        'response_data': response_data
                    }
            else:
                print(f"❌ HTTP {response.status_code} error: {response.text}")
                logger.error(f"External API request failed with status {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout error when calling external API: {api_endpoint}")
            logger.error(f"Timeout error when calling external API: {api_endpoint}")
            return {
                'success': False,
                'error': 'Request timeout'
            }
        except requests.exceptions.RequestException as e:
            print(f"🌐 Request error when calling external API: {str(e)}")
            logger.error(f"Request error when calling external API: {str(e)}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            print(f"💥 Unexpected error when calling external API: {str(e)}")
            logger.error(f"Unexpected error when calling external API: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _save_meditation_file(self, user, ritual_type_name, file_data, file_name):
        """
        Save meditation file and create MeditationGenerate record
        
        Args:
            user: The authenticated user
            ritual_type_name: Name of the ritual type
            file_data: File data or URL from external API
            file_name: Name for the file
            
        Returns:
            MeditationGenerate: Created meditation record
        """
        try:
            # Get or create RitualType
            ritual_type, created = RitualType.objects.get_or_create(
                name=ritual_type_name,
                defaults={'description': f'External meditation for {ritual_type_name}'}
            )
            
            # Create a placeholder Rituals record for the meditation
            ritual = Rituals.objects.create(
                name=f"{ritual_type_name} Meditation",
                description=f"Generated meditation for {ritual_type_name}",
                ritual_type='story',  # Default to story type
                tone='dreamy',  # Default tone
                voice='female',  # Default voice
                duration='2'  # Default duration
            )
            
            # Create MeditationGenerate record
            meditation = MeditationGenerate.objects.create(
                user=user,
                details=ritual,
                ritual_type=ritual_type
            )
            
            # If we have file data, save it
            if file_data:
                try:
                    # If file_data is a URL, download it
                    if file_data.startswith('http'):
                        file_response = requests.get(file_data, timeout=30)
                        if file_response.status_code == 200:
                            content = ContentFile(file_response.content, name=file_name)
                            meditation.file.save(file_name, content, save=True)
                        else:
                            logger.warning(f"Failed to download file from {file_data}")
                    else:
                        # If file_data is base64 or other format, handle accordingly
                        logger.warning(f"Unsupported file_data format: {type(file_data)}")
                        
                except Exception as e:
                    logger.error(f"Error saving meditation file: {str(e)}")
                    # Continue without file - meditation record is still created
            
            return meditation
            
        except Exception as e:
            logger.error(f"Error creating meditation record: {str(e)}")
            raise



