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