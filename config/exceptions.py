from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
import logging

logger = logging.getLogger(__name__)

# Custom API Exceptions
class PlanTypeNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Plan type not found.'
    default_code = 'plan_type_not_found'

class AuthenticationRequiredError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication required.'
    default_code = 'authentication_required'

class SubscriptionRequiredError(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Valid subscription required.'
    default_code = 'subscription_required'

class TrialExpiredError(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Free trial has expired. Please upgrade to continue.'
    default_code = 'trial_expired'

class MeditationGenerationError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to generate meditation. Please try again.'
    default_code = 'meditation_generation_failed'

def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides appropriate HTTP status codes
    instead of always returning 500 errors.
    """
    
    # Call the default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # If DRF handled it, return the response
        return response
    
    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        logger.error(f"Django ValidationError: {exc}")
        return Response({
            'error': 'Validation error occurred',
            'detail': str(exc),
            'code': 'validation_error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle DRF ValidationError with custom codes
    if isinstance(exc, DRFValidationError):
        # Check for custom error codes in the exception
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            # Look for specific error codes
            if 'plan_type' in exc.detail:
                if 'missing_plan_type' in str(exc.detail):
                    return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
                elif 'invalid_plan_type' in str(exc.detail):
                    return Response(exc.detail, status=status.HTTP_404_NOT_FOUND)
                elif 'unknown_plan_type' in str(exc.detail):
                    return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
            
            if 'user' in exc.detail and 'authentication_required' in str(exc.detail):
                return Response(exc.detail, status=status.HTTP_401_UNAUTHORIZED)
            
            if 'subscription' in exc.detail:
                if 'trial_expired' in str(exc.detail):
                    return Response(exc.detail, status=status.HTTP_402_PAYMENT_REQUIRED)
                elif 'no_subscription' in str(exc.detail):
                    return Response(exc.detail, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            if 'error' in exc.detail and 'creation_failed' in str(exc.detail):
                return Response(exc.detail, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Default for DRF ValidationError
        return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle other exceptions
    logger.error(f"Unhandled exception: {exc}")
    return Response({
        'error': 'An unexpected error occurred',
        'detail': str(exc) if str(exc) else 'Internal server error',
        'code': 'internal_error'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    

class ExternalMeditationService:
    """
    Service for handling external meditation API requests.
    
    Maps plan_type IDs to external API endpoints, transforms request data to match the external API format,
    and saves returned MP3 files to the MeditationGenerate model.
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
            'age_range': 'age_range',
            'gender': 'name'  # Map gender to name to satisfy external API requirement
        }
    
    def process_meditation_request(self, user, validated_data):
        """
        Process meditation request and send to appropriate external API.
        
        Args:
            user: The authenticated user.
            validated_data: Validated data from ExternalMeditationSerializer.
            
        Returns:
            dict: Response with success status, message, and file details.
        """
        try:
            # Get plan type from validated data
            plan_type_id = validated_data.get('plan_type')
            
            # Get the ritual type name from the plan_type ID
            try:
                ritual_type = RitualType.objects.get(id=plan_type_id)
                ritual_type_name = ritual_type.name
            except RitualType.DoesNotExist:
                return {
                    "success": False,
                    "message": f"Plan type with ID {plan_type_id} does not exist",
                    "plan_type": f"ID: {plan_type_id}",
                    "ritual_type_name": None
                }
            
            # Get the appropriate API endpoint based on ritual type name
            api_endpoint = self._get_api_endpoint(ritual_type_name)
            
            if not api_endpoint:
                return {
                    "success": False,
                    "message": f"No API endpoint found for ritual type: {ritual_type_name}",
                    "plan_type": ritual_type_name,
                    "ritual_type_name": ritual_type_name
                }
            
            # Test API connectivity first
            if not self._test_api_connectivity(api_endpoint):
                # Save the meditation record without file
                meditation_record = self._save_meditation_file(
                    user=user,
                    ritual_type_name=ritual_type_name,
                    file_data=None,
                    file_name=None
                )
                
                # Build the full URL for the file
                file_url = None
                if meditation_record.file:
                    from django.conf import settings
                    # Get the base URL from settings or construct it
                    base_url = getattr(settings, 'BASE_URL', 'http://31.97.98.47:9000')
                    file_url = f"{base_url}{meditation_record.file.url}"
                
                return {
                    "success": True,
                    "message": "Meditation record created (external API unavailable)",
                    "plan_type": ritual_type_name,
                    "endpoint_used": api_endpoint,
                    "api_response": {"error": "API not reachable"},
                    "file_url": file_url,
                    "meditation_id": meditation_record.id,
                    "ritual_type_name": ritual_type_name,
                    "warning": "External API was unavailable, meditation created without audio file"
                }
            
            # Transform data for external API
            external_api_data = self._transform_data_for_external_api(validated_data)
            
            # Make request to external API with retries
            try:
                api_response = self._make_external_api_request(api_endpoint, external_api_data, ritual_type_name)
            except UnicodeDecodeError as e:
                return {
                    "success": False,
                    "message": f"Encoding error in API request: {str(e)}",
                    "plan_type": ritual_type_name,
                    "endpoint_used": api_endpoint,
                    "ritual_type_name": ritual_type_name
                }
            
            if not api_response.get('success'):
                # Handle timeout or connection errors
                if 'timeout' in api_response.get('error', '').lower() or 'connection' in api_response.get('error', '').lower():
                    # Save the meditation record without file
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
            
            # Safety check for api_response
            if api_response is None:
                return {
                    "success": False,
                    "message": "Internal error: API response is None",
                    "plan_type": ritual_type_name,
                    "endpoint_used": api_endpoint,
                    "ritual_type_name": ritual_type_name
                }
            
            try:
                # Create filename using ritual type name
                safe_ritual_name = ritual_type_name.replace(' ', '_').lower()
                default_filename = f"{safe_ritual_name}_{int(timezone.now().timestamp())}.mp3"
                
                meditation_record = self._save_meditation_file(
                    user=user,
                    ritual_type_name=ritual_type_name,
                    file_data=api_response.get('file_data') if api_response else None,
                    file_name=api_response.get('file_name', default_filename) if api_response else default_filename
                )
                
                # Build the full URL for the file
                file_url = None
                try:
                    if meditation_record.file:
                        from django.conf import settings
                        # Get the base URL from settings or construct it
                        base_url = getattr(settings, 'BASE_URL', 'http://31.97.98.47:9000')
                        file_url = f"{base_url}{meditation_record.file.url}"
                except Exception as url_error:
                    file_url = None
                
                # Prepare safe api_response for serialization
                safe_api_response = None
                try:
                    if api_response:
                        # Create a safe copy without binary data
                        safe_api_response = {
                            'success': api_response.get('success'),
                            'file_name': api_response.get('file_name'),
                            'response_data': api_response.get('response_data'),
                            'error': api_response.get('error')
                        }
                except Exception as serialize_error:
                    safe_api_response = {'error': 'Could not serialize response'}
                
                return {
                    "success": True,
                    "message": "Meditation generated successfully",
                    "plan_type": ritual_type_name,
                    "endpoint_used": api_endpoint,
                    "api_response": safe_api_response,
                    "file_url": file_url,
                    "meditation_id": meditation_record.id,
                    "ritual_type_name": ritual_type_name
                }
            except UnicodeDecodeError as e:
                # Prepare safe api_response for serialization
                safe_api_response = None
                try:
                    if api_response:
                        safe_api_response = {
                            'success': api_response.get('success'),
                            'file_name': api_response.get('file_name'),
                            'response_data': api_response.get('response_data'),
                            'error': api_response.get('error')
                        }
                except Exception:
                    safe_api_response = {'error': 'Could not serialize response'}
                
                return {
                    "success": False,
                    "message": f"Encoding error saving meditation: {str(e)}",
                    "plan_type": ritual_type_name,
                    "endpoint_used": api_endpoint,
                    "api_response": safe_api_response,
                    "ritual_type_name": ritual_type_name
                }
            except Exception as save_error:
                # Prepare safe api_response for serialization
                safe_api_response = None
                try:
                    if api_response:
                        safe_api_response = {
                            'success': api_response.get('success'),
                            'file_name': api_response.get('file_name'),
                            'response_data': api_response.get('response_data'),
                            'error': api_response.get('error')
                        }
                except Exception:
                    safe_api_response = {'error': 'Could not serialize response'}
                
                return {
                    "success": False,
                    "message": f"Error saving meditation file: {str(save_error)}",
                    "plan_type": ritual_type_name,
                    "endpoint_used": api_endpoint,
                    "api_response": safe_api_response,
                    "ritual_type_name": ritual_type_name
                }
            
        except UnicodeDecodeError as e:
            return {
                "success": False,
                "message": f"Encoding error: {str(e)}",
                "plan_type": validated_data.get('plan_type', 'Unknown'),
                "ritual_type_name": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "plan_type": validated_data.get('plan_type', 'Unknown'),
                "ritual_type_name": None
            }
    
    def _get_api_endpoint(self, ritual_type_name):
        """
        Get the appropriate API endpoint based on ritual type name.
        
        Args:
            ritual_type_name: Name of the ritual type.
            
        Returns:
            str: API endpoint URL or None if not found.
        """
        return self.api_endpoints.get(ritual_type_name)
    
    def _transform_data_for_external_api(self, validated_data):
        """
        Transform our data format to match external API requirements.
        
        Args:
            validated_data: Validated data from serializer.
            
        Returns:
            dict: Data formatted for external API.
        """
        external_data = {}
        
        # Map fields according to the mapping dictionary
        for our_field, external_field in self.field_mappings.items():
            if our_field in validated_data:
                external_data[external_field] = validated_data[our_field]
        
        # Add missing required fields that are not in our mapping
        # The external API expects these exact field names based on the curl request
        if 'name' not in external_data:
            # Use gender as name since that's what we have
            external_data['name'] = validated_data.get('gender', 'string')
        
        if 'check_in' not in external_data:
            # Add check_in field as required by external API
            external_data['check_in'] = 'string'
        
        # Validate required fields for external API
        required_fields = ['name', 'goals', 'dreamlife', 'dream_activities', 'ritual_type', 'tone', 'voice', 'length', 'check_in']
        for field in required_fields:
            if field not in external_data:
                external_data[field] = "string"  # Set default string for missing fields
        
        # Handle special transformations for external API format
        if 'ritual_type' in external_data:
            external_data['ritual_type'] = external_data['ritual_type'].capitalize()
        
        if 'tone' in external_data:
            external_data['tone'] = external_data['tone'].capitalize()
        
        if 'voice' in external_data:
            external_data['voice'] = external_data['voice'].capitalize()
        
        if 'length' in external_data:
            try:
                external_data['length'] = int(external_data['length'])
            except (ValueError, TypeError):
                external_data['length'] = 2  # Default to 2 minutes
        
        return external_data
    
    def _test_api_connectivity(self, api_endpoint):
        """
        Test basic connectivity to the external API endpoint.
        
        Args:
            api_endpoint: The API endpoint URL.
            
        Returns:
            bool: True if API is reachable, False otherwise.
        """
        try:
            # Try a simple GET request to see if the server is reachable
            response = requests.get(api_endpoint, timeout=10)
            
            if response.status_code in [200, 404, 405, 422]:  # Any response means server is reachable
                return True
            else:
                return False
                
        except requests.exceptions.ConnectionError as e:
            return False
        except requests.exceptions.Timeout as e:
            return False
        except Exception as e:
            return False

    def _make_external_api_request(self, api_endpoint, data, ritual_type_name):
        """
        Make HTTP request to external API with retry logic.
        
        Args:
            api_endpoint: The API endpoint URL.
            data: Data to send to the API.
            ritual_type_name: Name of the ritual type for filename generation.
            
        Returns:
            dict: Response from external API.
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        # Helper function to create filename with ritual type name
        def create_filename():
            safe_ritual_name = ritual_type_name.replace(' ', '_').lower()
            return f"{safe_ritual_name}_{int(timezone.now().timestamp())}.mp3"
        
        for attempt in range(max_retries):
            try:
                # Increase timeout to 60 seconds and add better headers
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, audio/mpeg, */*',
                    'User-Agent': 'Vela-Meditation-App/1.0'
                }
                
                response = requests.post(
                    api_endpoint,
                    json=data,
                    headers=headers,
                    timeout=60  # Increased from 30 to 60 seconds
                )
                
                # Early detection of binary data - if we see binary markers, treat as binary immediately
                if response.content:
                    # Check if content contains null bytes (binary indicator)
                    high_bytes = sum(1 for b in response.content[:100] if b > 127)
                    
                    # Early detection of binary data - if we see binary markers, treat as binary immediately
                    if (b'\x00' in response.content[:100] or 
                        high_bytes > 50 or 
                        response.content.startswith(b'ID3')):
                        return {
                            'success': True,
                            'file_data': response.content,  # Return binary data
                            'file_name': create_filename(),
                            'response_data': {'file_type': 'binary_audio'}
                        }
                
                if response.status_code == 200:
                    # Check if response has content
                    if not response.content:
                        return {
                            'success': False,
                            'error': 'Empty response from external API - server returned no content'
                        }
                    
                    # Check if response is binary (MP3 file) - do this first to avoid UTF-8 issues
                    content_type = response.headers.get('content-type', '').lower()
                    is_binary = (
                        'audio' in content_type or 
                        'mpeg' in content_type or 
                        response.content.startswith(b'ID3') or
                        len(response.content) > 1000 or
                        b'\x00' in response.content[:100] or  # Null bytes indicate binary
                        sum(1 for b in response.content[:100] if b > 127) > 50  # Many high bytes indicate binary
                    )
                    
                    # If binary, handle immediately without any text operations
                    if is_binary:
                        return {
                            'success': True,
                            'file_data': response.content,  # Return binary data
                            'file_name': create_filename(),
                            'response_data': {'file_type': 'binary_audio'}
                        }
                    
                    # Only try to parse as JSON if it's not binary
                    try:
                        # Check if response is actually JSON before trying to parse
                        if response.content.startswith(b'{') or response.content.startswith(b'['):
                            # Additional check for binary data disguised as JSON
                            if b'\x00' in response.content[:100] or sum(1 for b in response.content[:100] if b > 127) > 50:
                                if response.content.startswith(b'ID3') or len(response.content) > 1000:
                                    return {
                                        'success': True,
                                        'file_data': response.content,  # Return binary data
                                        'file_name': create_filename(),
                                        'response_data': {'file_type': 'binary_audio'}
                                    }
                                else:
                                    return {
                                        'success': False,
                                        'error': 'Response contains binary data but is not recognized as audio'
                                    }
                            
                            try:
                                response_data = response.json()
                            except UnicodeDecodeError as e:
                                # This might be binary data disguised as JSON
                                if response.content.startswith(b'ID3') or len(response.content) > 1000:
                                    return {
                                        'success': True,
                                        'file_data': response.content,  # Return binary data
                                        'file_name': create_filename(),
                                        'response_data': {'file_type': 'binary_audio'}
                                    }
                                else:
                                    return {
                                        'success': False,
                                        'error': f'Unicode decode error in JSON parsing: {str(e)}'
                                    }
                        else:
                            # Not JSON, might be binary
                            if response.content.startswith(b'ID3') or len(response.content) > 1000:
                                return {
                                    'success': True,
                                    'file_data': response.content,  # Return binary data
                                    'file_name': create_filename(),
                                    'response_data': {'file_type': 'binary_audio'}
                                }
                            else:
                                return {
                                    'success': False,
                                    'error': 'Invalid response format from external API'
                                }
                        
                        # Check if the response contains file data
                        if 'file' in response_data or 'file_url' in response_data:
                            file_url = response_data.get('file_url') or response_data.get('file')
                            return {
                                'success': True,
                                'file_data': file_url,
                                'file_name': create_filename(),
                                'response_data': response_data
                            }
                        else:
                            return {
                                'success': True,
                                'file_data': None,
                                'file_name': create_filename(),
                                'response_data': response_data
                            }
                    except json.JSONDecodeError as json_error:
                        # If JSON parsing fails, check if it might be binary data
                        if (response.content.startswith(b'ID3') or 
                            len(response.content) > 1000 or
                            b'\x00' in response.content[:100] or
                            sum(1 for b in response.content[:100] if b > 127) > 50):
                            return {
                                'success': True,
                                'file_data': response.content,  # Return binary data
                                'file_name': create_filename(),
                                'response_data': {'file_type': 'binary_audio'}
                            }
                        else:
                            return {
                                'success': False,
                                'error': f'Invalid JSON response from external API: {str(json_error)}'
                            }
                    except UnicodeDecodeError as unicode_error:
                        # Handle Unicode decode errors (binary data being treated as text)
                        if (response.content.startswith(b'ID3') or 
                            len(response.content) > 1000 or
                            b'\x00' in response.content[:100] or
                            sum(1 for b in response.content[:100] if b > 127) > 50):
                            return {
                                'success': True,
                                'file_data': response.content,  # Return binary data
                                'file_name': create_filename(),
                                'response_data': {'file_type': 'binary_audio'}
                            }
                        else:
                            return {
                                'success': False,
                                'error': f'Unicode decode error: {str(unicode_error)}'
                            }
                elif response.status_code == 422:
                    try:
                        # Check if response is actually JSON before trying to parse
                        if response.content.startswith(b'{') or response.content.startswith(b'['):
                            # Additional check for binary data disguised as JSON
                            if b'\x00' in response.content[:100] or sum(1 for b in response.content[:100] if b > 127) > 50:
                                return {
                                    'success': False,
                                    'error': f"HTTP 422: Validation error - Binary response"
                                }
                            
                            try:
                                error_detail = response.json().get('detail', 'Validation error')
                                return {
                                    'success': False,
                                    'error': f"HTTP 422: Validation error - {error_detail}"
                                }
                            except UnicodeDecodeError as e:
                                return {
                                    'success': False,
                                    'error': f"HTTP 422: Validation error - Binary response"
                                }
                        else:
                            return {
                                'success': False,
                                'error': f"HTTP 422: Validation error - Non-JSON response"
                            }
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        return {
                            'success': False,
                            'error': f"HTTP 422: Validation error - Invalid response"
                        }
                else:
                    # Handle error response
                    try:
                        # Check if response is binary before trying to decode as text
                        content_type = response.headers.get('content-type', '').lower()
                        if ('audio' in content_type or 
                            'mpeg' in content_type or 
                            response.content.startswith(b'ID3') or
                            b'\x00' in response.content[:100] or
                            sum(1 for b in response.content[:100] if b > 127) > 50):
                            return {
                                'success': False,
                                'error': f"HTTP {response.status_code}: Binary audio response received"
                            }
                    except UnicodeDecodeError as e:
                        pass
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.reason}"
                    }
                    
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': 'Request timeout after retries'
                    }
            except requests.exceptions.ConnectionError as e:
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f'Connection failed: {str(e)}'
                    }
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f'Request failed: {str(e)}'
                    }
            except UnicodeDecodeError as e:
                return {
                    'success': False,
                    'error': f'Unicode decode error: {str(e)}'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Unexpected error: {str(e)}'
                }
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    def _save_meditation_file(self, user, ritual_type_name, file_data, file_name):
        """
        Save meditation file and create MeditationGenerate record.
        
        Args:
            user: The authenticated user (can be None for unauthenticated requests).
            ritual_type_name: Name of the ritual type.
            file_data: File data or URL from external API.
            file_name: Name for the file.
            
        Returns:
            MeditationGenerate: Created meditation record.
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
                ritual_type='story',
                tone='dreamy',
                voice='female',
                duration='2'
            )
            
            # Handle the case where user is None (unauthenticated request)
            if user is None:
                # For unauthenticated requests, we'll create a meditation record without a user
                # This requires the user field to be nullable in the model
                # For now, let's create a default anonymous user
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # Try to get or create an anonymous user
                try:
                    anonymous_user = User.objects.get(username='anonymous')
                except User.DoesNotExist:
                    # Create an anonymous user for unauthenticated requests
                    anonymous_user = User.objects.create(
                        username='anonymous',
                        email='anonymous@vela.com',
                        first_name='Anonymous',
                        last_name='User'
                    )
                
                user = anonymous_user
            
            # Create MeditationGenerate record
            meditation = MeditationGenerate.objects.create(
                user=user,
                details=ritual,
                ritual_type=ritual_type
            )
            
            # If we have file data, save it
            if file_data and file_name:
                try:
                    # Check if file_data is binary data (from external API)
                    if isinstance(file_data, bytes):
                        try:
                            content = ContentFile(file_data, name=file_name)
                            meditation.file.save(file_name, content, save=True)
                        except Exception as save_error:
                            # Continue without the file
                            pass
                    # If file_data is a URL, download it
                    elif isinstance(file_data, str) and file_data.startswith('http'):
                        try:
                            file_response = requests.get(file_data, timeout=30)
                            if file_response.status_code == 200:
                                # Check if the downloaded content is binary audio
                                content_type = file_response.headers.get('content-type', '').lower()
                                if 'audio' in content_type or 'mpeg' in content_type or file_response.content.startswith(b'ID3'):
                                    try:
                                        content = ContentFile(file_response.content, name=file_name)
                                        meditation.file.save(file_name, content, save=True)
                                    except Exception as save_error:
                                        # Continue without the file
                                        pass
                        except Exception as e:
                            pass
                except UnicodeDecodeError as e:
                    # This might happen if binary data is being treated as text somewhere
                    pass
                except Exception as e:
                    pass
            
            return meditation
            
        except Exception as e:
            raise