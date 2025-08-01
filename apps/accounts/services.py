import requests
import json
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from datetime import datetime
import os

from apps.accounts.models import RitualType, Rituals, MeditationGenerate
from apps.accounts.generate.functions import sleep_function, spark_function, calm_function, dream_function

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
    """Service class to handle meditation generation using local functions"""
    
    def __init__(self):
        # Keep the API endpoints for reference, but we'll use local functions
        self.api_endpoints = {
            "Sleep Manifestation": "http://31.97.98.47:8000/sleep",
            "Morning Spark": "http://31.97.98.47:8000/spark", 
            "Calming Reset": "http://31.97.98.47:8000/calm",
            "Dream Visualizer": "http://31.97.98.47:8000/dream"
        }
        
        # Map plan types to local functions
        self.function_mapping = {
            "Sleep Manifestation": sleep_function,
            "Morning Spark": spark_function, 
            "Calming Reset": calm_function,
            "Dream Visualizer": dream_function
        }
    
    def generate_local_meditation(self, plan_type, validated_data):
        """Generate meditation using local functions"""
        try:
            # Get the appropriate function
            generation_function = self.function_mapping.get(plan_type)
            if not generation_function:
                raise ValueError(f"Unknown plan type: {plan_type}")
            
            # Prepare parameters for the function
            name = validated_data.get('gender', 'User')
            goals = validated_data.get('goals', '')
            dreamlife = validated_data.get('dream', '')
            dream_activities = validated_data.get('happiness', '')
            
            # Map ritual type
            ritual_type_mapping = {
                'story': 'Story',
                'guided_meditations': 'Guided'
            }
            ritual_type = ritual_type_mapping.get(validated_data.get('ritual_type', 'story'), 'Story')
            
            # Map tone
            tone_mapping = {
                'dreamy': 'Dreamy',
                'asmr': 'ASMR'
            }
            tone = tone_mapping.get(validated_data.get('tone', 'dreamy'), 'Dreamy')
            
            # Map voice
            voice_mapping = {
                'male': 'male',
                'female': 'female'
            }
            voice = voice_mapping.get(validated_data.get('voice', 'female'), 'female')
            
            # Get length
            length = int(validated_data.get('duration', 2))
            if length not in [2, 5, 10]:
                length = 2
            
            logger.info(f"Generating local meditation for {plan_type}")
            logger.info(f"Parameters: name={name}, ritual_type={ritual_type}, tone={tone}, voice={voice}, length={length}")
            
            # Generate the meditation audio
            audio_data = generation_function(
                name=name,
                goals=goals,
                dreamlife=dreamlife,
                dream_activities=dream_activities,
                ritual_type=ritual_type,
                tone=tone,
                voice=voice,
                length=length,
                check_in=""
            )
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating local meditation: {str(e)}")
            raise
    
    def save_meditation_file(self, user, plan_type, audio_data, response_data):
        """Save the meditation file and create a meditation record"""
        try:
            # Get the ritual type
            ritual_type = RitualType.objects.get(name=plan_type)
            
            # Create a ritual record
            ritual = Rituals.objects.create(
                name=f"{plan_type} Meditation",
                description=f"Generated meditation for {plan_type}",
                ritual_type=response_data.get('ritual_type', 'Story'),
                tone=response_data.get('tone', 'Dreamy'),
                voice=response_data.get('voice', 'Female'),
                duration=str(response_data.get('duration', 2))
            )
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"local_meditation_{plan_type.lower().replace(' ', '_')}_{timestamp}.mp3"
            
            # Create file content from audio data or placeholder
            if audio_data:
                file_content = ContentFile(audio_data, name=filename)
            else:
                # Create placeholder file when audio_data is None
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
                ritual_type=response_data.get('ritual_type', 'Story'),
                tone=response_data.get('tone', 'Dreamy'),
                voice=response_data.get('voice', 'Female'),
                duration=str(response_data.get('duration', 2))
            )
            meditation = MeditationGenerate.objects.create(
                user=user,
                details=ritual,
                ritual_type=ritual_type
            )
            return meditation
    
    def create_placeholder_file(self, filename):
        """Create a placeholder file when generation fails"""
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
        """Process a complete meditation request using local generation"""
        try:
            # Extract data
            plan_type = validated_data['plan_type']
            
            logger.info(f"Processing meditation request for {plan_type}")
            
            try:
                # Generate meditation using local functions
                audio_data = self.generate_local_meditation(plan_type, validated_data)
                
                # Save the meditation file
                meditation_record = self.save_meditation_file(
                    user=user,
                    plan_type=plan_type,
                    audio_data=audio_data,
                    response_data=validated_data
                )
                
                return {
                    "success": True,
                    "message": f"Successfully generated {plan_type} meditation",
                    "plan_type": plan_type,
                    "generation_method": "local",
                    "file_url": f"{settings.MEDITATION_API_CONFIG['BASE_URL']}{meditation_record.file.url}" if meditation_record.file else None,
                    "meditation_id": meditation_record.id
                }
                
            except Exception as e:
                logger.error(f"Error in local meditation generation: {str(e)}")
                
                # Create meditation record with placeholder even on generation error
                meditation_record = self.save_meditation_file(
                    user=user,
                    plan_type=plan_type,
                    audio_data=None,
                    response_data=validated_data
                )
                
                return {
                    "success": False,
                    "error": f"Local generation failed: {str(e)}",
                    "plan_type": plan_type,
                    "generation_method": "placeholder",
                    "file_url": f"{settings.MEDITATION_API_CONFIG['BASE_URL']}{meditation_record.file.url}" if meditation_record.file else None,
                    "meditation_id": meditation_record.id
                }
                
        except Exception as e:
            logger.error(f"Unexpected error in process_meditation_request: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
