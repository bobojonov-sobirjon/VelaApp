from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

def get_user_from_token(token_key):
    """
    Get user from JWT token
    
    Args:
        token_key (str): The JWT token string
        
    Returns:
        User: The authenticated user or AnonymousUser if token is invalid
    """
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token_key)
        user = jwt_auth.get_user(validated_token)
        return user
    except (InvalidToken, TokenError, AuthenticationFailed):
        return AnonymousUser()
    except Exception:
        return AnonymousUser()

def get_user_from_request(request):
    """
    Get user from request (either authenticated or from token)
    
    Args:
        request: The HTTP request object
        
    Returns:
        User: The authenticated user or AnonymousUser if not authenticated
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    
    # Try to get user from Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        return get_user_from_token(token)
    
    return AnonymousUser()

def get_or_create_user_detail(user):
    """
    Get or create CustomUserDetail for a user
    
    Args:
        user: The user object
        
    Returns:
        CustomUserDetail: The user detail object
    """
    from apps.accounts.models import CustomUserDetail
    
    if user.is_anonymous:
        return None
    
    user_detail, created = CustomUserDetail.objects.get_or_create(
        user=user,
        defaults={
            'gender': '',
            'dream': '',
            'goals': '',
            'age_range': '',
            'happiness': ''
        }
    )
    return user_detail 