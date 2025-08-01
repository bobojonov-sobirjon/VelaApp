import requests
import json
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from datetime import datetime
import os

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
    """Service class to handle external meditation API operations and file management"""
    
    def __init__(self):
        self.api_endpoints = {
            "Sleep Manifestation": "http://31.97.98.47:8000/sleep",
            "Morning Spark": "http://31.97.98.47:8000/spark", 
            "Calming Reset": "http://31.97.98.47:8000/calm",
            "Dream Visualizer": "http://31.97.98.47:8000/dream"
        }
    
    def call_external_api(self, plan_type, payload):
        """Call external meditation API"""
        try:
            api_endpoint = self.api_endpoints.get(plan_type)
            if not api_endpoint:
                raise ValueError(f"Unknown plan type: {plan_type}")
            
            headers = {'Content-Type': 'application/json'}
            logger.info(f"Sending request to {api_endpoint}")
            logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
            logger.info(f"Request headers: {headers}")
            
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=15
            )
            
            logger.info(f"External API Response Status: {response.status_code}")
            logger.info(f"External API Response Headers: {dict(response.headers)}")
            logger.info(f"External API Response Body: {response.text}")
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error when calling {api_endpoint}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when calling {api_endpoint}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling external API: {str(e)}")
            raise
    
    def save_meditation_file(self, user, plan_type, api_response, response_data, binary_data=None):
        """Save the meditation file and create a meditation record"""
        try:
            # Get the ritual type
            ritual_type = RitualType.objects.get(name=plan_type)
            
            # Create a ritual record
            ritual = Rituals.objects.create(
                name=f"{plan_type} Meditation",
                description=f"Generated meditation for {plan_type}",
                ritual_type=response_data.get('ritual_type', 'story'),
                tone=response_data.get('tone', 'dreamy'),
                voice=response_data.get('voice', 'female'),
                duration=str(response_data.get('duration', '2'))
            )
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"external_meditation_{plan_type.lower().replace(' ', '_')}_{timestamp}.mp3"
            
            # Create file content
            if binary_data:
                # Use binary data from response
                file_content = ContentFile(binary_data, name=filename)
            else:
                # Try to extract file data from API response
                if 'file' in api_response and api_response['file']:
                    import base64
                    try:
                        # Decode base64 file data if present
                        file_data = base64.b64decode(api_response['file'])
                        file_content = ContentFile(file_data, name=filename)
                    except:
                        # Fallback to placeholder
                        file_content = self.create_placeholder_file(filename)
                else:
                    # Create placeholder file
                    file_content = self.create_placeholder_file(filename)
            
            # Create meditation record
            with transaction.atomic():
                meditation = MeditationGenerate.objects.create(
                    user=user,
                    details=ritual,
                    ritual_type=ritual_type,
                    file=file_content
                )
            
            logger.info(f"Saved meditation file: {filename} for user {user.id}")
            return meditation
            
        except Exception as e:
            logger.error(f"Error saving meditation file: {str(e)}")
            # Return a minimal meditation record without file
            ritual_type = RitualType.objects.get(name=plan_type)
            ritual = Rituals.objects.create(
                name=f"{plan_type} Meditation",
                description=f"Generated meditation for {plan_type}",
                ritual_type=response_data.get('ritual_type', 'story'),
                tone=response_data.get('tone', 'dreamy'),
                voice=response_data.get('voice', 'female'),
                duration=str(response_data.get('duration', '2'))
            )
            meditation = MeditationGenerate.objects.create(
                user=user,
                details=ritual,
                ritual_type=ritual_type
            )
            return meditation
    
    def create_placeholder_file(self, filename):
        """Create a placeholder file when external API doesn't return a file"""
        try:
            # Path to the default MP3 file
            default_mp3_path = os.path.join(os.path.dirname(__file__), 'muzic', 'sleep_manifestation.mp3')
            
            with open(default_mp3_path, 'rb') as f:
                audio_data = f.read()
            return ContentFile(audio_data, name=filename)
            
        except Exception as e:
            logger.error(f"Failed to load default placeholder MP3: {str(e)}")
            # Fallback: return a minimal ContentFile with error message
            content = f"Placeholder audio unavailable. Error: {str(e)}"
            return ContentFile(content.encode('utf-8'), name=filename)
    
    def process_meditation_request(self, user, validated_data):
        """Process a complete meditation request"""
        try:
            # Extract data - plan_type is now the ritual type name from serializer validation
            plan_type = validated_data['plan_type']
            
            # Log the transformation being applied
            logger.info(f"Transforming data for external API...")
            logger.info(f"Input data: {json.dumps(validated_data, indent=2)}")
            logger.info(f"Plan type: {plan_type}")
            logger.info(f"API endpoint: {self.api_endpoints.get(plan_type)}")
            
            # Helper function to map values to external API format
            def map_to_external_format(value, field_type):
                if field_type == 'ritual_type':
                    mapping = {'story': 'Story', 'guided_meditations': 'Guided'}
                    return mapping.get(value, 'Story')
                elif field_type == 'tone':
                    mapping = {'dreamy': 'Dreamy', 'asmr': 'ASMR'}
                    return mapping.get(value, 'Dreamy')
                elif field_type == 'voice':
                    mapping = {'male': 'Male', 'female': 'Female'}
                    return mapping.get(value, 'Female')
                else:
                    return value
            
            # Try multiple payload formats for external API
            payload_formats = [
                # Format 1: Direct mapping with external API field names and proper capitalization
                {
                    "name": validated_data['gender'],
                    "dreamlife": validated_data['dream'],
                    "goals": validated_data['goals'],
                    "dream_activities": validated_data['age_range'],
                    "ritual_type": map_to_external_format(validated_data['ritual_type'], 'ritual_type'),
                    "tone": map_to_external_format(validated_data['tone'], 'tone'),
                    "voice": map_to_external_format(validated_data['voice'], 'voice'),
                    "length": int(validated_data['duration'])
                },
                # Format 2: Alternative field name for ritual type
                {
                    "name": validated_data['gender'],
                    "dreamlife": validated_data['dream'],
                    "goals": validated_data['goals'],
                    "dream_activities": validated_data['age_range'],
                    "type": map_to_external_format(validated_data['ritual_type'], 'ritual_type'),
                    "tone": map_to_external_format(validated_data['tone'], 'tone'),
                    "voice": map_to_external_format(validated_data['voice'], 'voice'),
                    "length": int(validated_data['duration'])
                },
                # Format 3: With check_in field using happiness data
                {
                    "name": validated_data['gender'],
                    "dreamlife": validated_data['dream'],
                    "goals": validated_data['goals'],
                    "dream_activities": validated_data['age_range'],
                    "ritual_type": map_to_external_format(validated_data['ritual_type'], 'ritual_type'),
                    "tone": map_to_external_format(validated_data['tone'], 'tone'),
                    "voice": map_to_external_format(validated_data['voice'], 'voice'),
                    "length": int(validated_data['duration']),
                    "check_in": validated_data.get('happiness', '')
                },
                # Format 4: Using original field names as they might be expected
                {
                    "gender": validated_data['gender'],
                    "dream": validated_data['dream'],
                    "goals": validated_data['goals'],
                    "age_range": validated_data['age_range'],
                    "happiness": validated_data.get('happiness', ''),
                    "ritual_type": map_to_external_format(validated_data['ritual_type'], 'ritual_type'),
                    "tone": map_to_external_format(validated_data['tone'], 'tone'),
                    "voice": map_to_external_format(validated_data['voice'], 'voice'),
                    "duration": validated_data['duration']
                }
            ]
            
            response = None
            successful_format = None
            
            for i, payload_format in enumerate(payload_formats):
                logger.info(f"Trying payload format {i+1}: {json.dumps(payload_format, indent=2)}")
                
                try:
                    response = self.call_external_api(plan_type, payload_format)
                    if response.status_code == 200:
                        successful_format = i+1
                        logger.info(f"✅ Payload format {i+1} succeeded!")
                        break
                    else:
                        logger.warning(f"❌ Payload format {i+1} failed with status {response.status_code}")
                        logger.warning(f"Response body: {response.text}")
                except Exception as e:
                    logger.error(f"❌ Payload format {i+1} failed with exception: {str(e)}")
            
            if not response:
                error_details = {
                    "message": "All payload formats failed",
                    "validated_data": validated_data,
                    "plan_type": plan_type,
                    "api_endpoint": self.api_endpoints.get(plan_type)
                }
                logger.error(f"All payload formats failed. Details: {json.dumps(error_details, indent=2)}")
                raise Exception("All payload formats failed")
            
            # Log which format succeeded
            if successful_format:
                logger.info(f"🎉 Successfully used payload format {successful_format} for {plan_type} API")
            
            # Process response
            if response.status_code == 200:
                try:
                    api_response = response.json()
                    meditation_record = self.save_meditation_file(
                        user=user,
                        plan_type=plan_type,
                        api_response=api_response,
                        response_data=validated_data
                    )
                    
                    return {
                        "success": True,
                        "message": f"Successfully sent request to {plan_type} API",
                        "plan_type": plan_type,
                        "endpoint_used": self.api_endpoints[plan_type],
                        "file_url": self._get_file_url(meditation_record) if meditation_record.file else None,
                        "meditation_id": meditation_record.id
                    }
                    
                except json.JSONDecodeError:
                    # Handle case where response is not JSON (might be binary file)
                    meditation_record = self.save_meditation_file(
                        user=user,
                        plan_type=plan_type,
                        api_response={"raw_response": response.text},
                        response_data=validated_data,
                        binary_data=response.content
                    )
                    
                    return {
                        "success": True,
                        "message": f"Successfully sent request to {plan_type} API",
                        "plan_type": plan_type,
                        "endpoint_used": self.api_endpoints[plan_type],
                        "file_url": self._get_file_url(meditation_record) if meditation_record.file else None,
                        "meditation_id": meditation_record.id
                    }
            else:
                # Even if external API fails, create a meditation record with placeholder
                meditation_record = self.save_meditation_file(
                    user=user,
                    plan_type=plan_type,
                    api_response={"error": response.text},
                    response_data=validated_data
                )
                
                return {
                    "success": False,
                    "error": f"External API returned status {response.status_code}",
                    "plan_type": plan_type,
                    "endpoint_used": self.api_endpoints[plan_type],
                    "file_url": self._get_file_url(meditation_record) if meditation_record.file else None,
                    "meditation_id": meditation_record.id
                }
                
        except requests.exceptions.Timeout:
            # Create meditation record with placeholder even on timeout
            meditation_record = self.save_meditation_file(
                user=user,
                plan_type=plan_type,
                api_response={"error": "Timeout"},
                response_data=validated_data
            )
            return {
                "success": False,
                "error": f"Timeout error when calling {plan_type} API",
                "plan_type": plan_type,
                "endpoint_used": self.api_endpoints[plan_type],
                "file_url": self._get_file_url(meditation_record) if meditation_record.file else None,
                "meditation_id": meditation_record.id
            }
            
        except requests.exceptions.RequestException as e:
            # Create meditation record with placeholder even on request error
            meditation_record = self.save_meditation_file(
                user=user,
                plan_type=plan_type,
                api_response={"error": str(e)},
                response_data=validated_data
            )
            return {
                "success": False,
                "error": f"Request error when calling {plan_type} API: {str(e)}",
                "plan_type": plan_type,
                "endpoint_used": self.api_endpoints[plan_type],
                "file_url": self._get_file_url(meditation_record) if meditation_record.file else None,
                "meditation_id": meditation_record.id
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in process_meditation_request: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _get_file_url(self, meditation_record):
        """Helper method to generate file URL with proper error handling"""
        try:
            base_url = getattr(settings, 'MEDITATION_API_CONFIG', {}).get('BASE_URL', '')
            if base_url and meditation_record.file:
                return f"{base_url}{meditation_record.file.url}"
            elif meditation_record.file:
                return meditation_record.file.url
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating file URL: {str(e)}")
            return None
