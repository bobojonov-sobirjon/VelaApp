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
    
    def create_meditation_file(self, user, validated_data):
        """Create meditation file and record - ALWAYS creates a file"""
        try:
            # Get the ritual type by ID
            plan_type_id = validated_data['plan_type']
            ritual_type = RitualType.objects.get(id=plan_type_id)
            
            # Create a ritual record
            ritual = Rituals.objects.create(
                name=f"{ritual_type.name} Meditation",
                description=f"Generated meditation for {ritual_type.name}",
                ritual_type=validated_data.get('ritual_type', 'story'),
                tone=validated_data.get('tone', 'dreamy'),
                voice=validated_data.get('voice', 'female'),
                duration=str(validated_data.get('duration', '2'))
            )
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meditation_{ritual_type.name.lower().replace(' ', '_')}_{timestamp}.mp3"
            
            # ALWAYS create a file - use placeholder MP3
            file_content = self.get_placeholder_audio(filename)
            
            # Create meditation record with file
            with transaction.atomic():
                meditation = MeditationGenerate.objects.create(
                    user=user,
                    details=ritual,
                    ritual_type=ritual_type,
                    file=file_content
                )
            
            logger.info(f"Created meditation file: {filename} for user {user.id}")
            return meditation
            
        except Exception as e:
            logger.error(f"Error creating meditation file: {str(e)}")
            raise
    
    def get_placeholder_audio(self, filename):
        """Get placeholder audio file"""
        try:
            # Path to the default MP3 file
            default_mp3_path = os.path.join(os.path.dirname(__file__), 'muzic', 'sleep_manifestation.mp3')
            
            with open(default_mp3_path, 'rb') as f:
                audio_data = f.read()
            return ContentFile(audio_data, name=filename)
            
        except Exception as e:
            logger.error(f"Failed to load placeholder MP3: {str(e)}")
            # Create a minimal audio file
            content = f"Audio file for meditation. Error: {str(e)}"
            return ContentFile(content.encode('utf-8'), name=filename)
    
    def get_file_url(self, meditation_record):
        """Generate file URL for API response"""
        try:
            if not meditation_record.file:
                return None
                
            # Use Django server URL for file serving
            django_server_url = getattr(settings, 'DJANGO_SERVER_URL', 'http://31.97.98.47:8080')
            
            # Remove trailing slash if present
            django_server_url = django_server_url.rstrip('/')
            file_url = meditation_record.file.url
            # Remove leading slash if present
            file_url = file_url.lstrip('/')
            
            return f"{django_server_url}/{file_url}"
                
        except Exception as e:
            logger.error(f"Error generating file URL: {str(e)}")
            return None
    
    def call_external_api(self, plan_type_name, payload):
        """Call external meditation API"""
        try:
            api_endpoint = self.api_endpoints.get(plan_type_name)
            if not api_endpoint:
                raise ValueError(f"Unknown plan type: {plan_type_name}")
            
            headers = {'Content-Type': 'application/json'}
            logger.info(f"Sending request to {api_endpoint}")
            logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"External API Response Status: {response.status_code}")
            logger.info(f"External API Response: {response.text}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error calling external API: {str(e)}")
            raise
    
    def process_meditation_request(self, user, validated_data):
        """Process meditation request with external API call"""
        try:
            # Get plan_type name from ID
            plan_type_id = validated_data['plan_type']
            try:
                ritual_type = RitualType.objects.get(id=plan_type_id)
                plan_type_name = ritual_type.name
            except RitualType.DoesNotExist:
                plan_type_name = "Morning Spark"  # Default fallback
            
            logger.info(f"Processing meditation request for plan_type_id: {plan_type_id} -> {plan_type_name}")
            logger.info(f"User: {user.id}")
            logger.info(f"Data: {json.dumps(validated_data, indent=2)}")
            
            # Map the data to external API format
            external_payload = {
                "name": validated_data['gender'],
                "goals": validated_data['goals'],
                "dreamlife": validated_data['dream'],
                "dream_activities": validated_data['happiness'],
                "ritual_type": validated_data['ritual_type'].title(),  # "story" -> "Story"
                "tone": validated_data['tone'].title(),  # "dreamy" -> "Dreamy"
                "voice": validated_data['voice'].title(),  # "female" -> "Female"
                "length": int(validated_data['duration']),  # "2" -> 2
                "check_in": "string"
            }
            
            logger.info(f"External API payload: {json.dumps(external_payload, indent=2)}")
            
            # Call external API
            try:
                api_response = self.call_external_api(plan_type_name, external_payload)
                
                if api_response.status_code == 200:
                    # Success - create meditation record with external API response
                    meditation_record = self.create_meditation_file(user, validated_data)
                    file_url = self.get_file_url(meditation_record)
                    
                    return {
                        "success": True,
                        "message": f"Successfully called {plan_type_name} API",
                        "plan_type": plan_type_name,
                        "api_endpoint": self.api_endpoints[plan_type_name],
                        "api_status": api_response.status_code,
                        "api_response": api_response.text,
                        "file_url": file_url,
                        "meditation_id": meditation_record.id,
                        "ritual_id": meditation_record.details.id,
                        "ritual_type_id": meditation_record.ritual_type.id,
                        "external_payload": external_payload
                    }
                else:
                    # API call failed but still create meditation record
                    meditation_record = self.create_meditation_file(user, validated_data)
                    file_url = self.get_file_url(meditation_record)
                    
                    return {
                        "success": False,
                        "error": f"External API returned status {api_response.status_code}",
                        "plan_type": plan_type_name,
                        "api_endpoint": self.api_endpoints[plan_type_name],
                        "api_status": api_response.status_code,
                        "api_response": api_response.text,
                        "file_url": file_url,
                        "meditation_id": meditation_record.id,
                        "ritual_id": meditation_record.details.id,
                        "ritual_type_id": meditation_record.ritual_type.id,
                        "external_payload": external_payload
                    }
                    
            except Exception as e:
                # External API failed but still create meditation record
                meditation_record = self.create_meditation_file(user, validated_data)
                file_url = self.get_file_url(meditation_record)
                
                return {
                    "success": False,
                    "error": f"External API call failed: {str(e)}",
                    "plan_type": plan_type_name,
                    "api_endpoint": self.api_endpoints.get(plan_type_name),
                    "file_url": file_url,
                    "meditation_id": meditation_record.id,
                    "ritual_id": meditation_record.details.id,
                    "ritual_type_id": meditation_record.ritual_type.id,
                    "external_payload": external_payload
                }
                
        except Exception as e:
            logger.error(f"Error in process_meditation_request: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create meditation: {str(e)}"
            }
