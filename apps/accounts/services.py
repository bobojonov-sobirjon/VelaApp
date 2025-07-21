import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import urlencode

from apps.accounts.models import CustomUser


class GoogleLoginService:
    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def get_authorization_url(self):
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        }
        auth_url = f"{self.AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return auth_url

    def get_tokens(self, code):
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        try:
            response = requests.post(self.TOKEN_URL, data=data)
            response_data = response.json()
            return response_data
        except Exception as e:
            return {"error": f"Token exchange error: {str(e)}"}

    def get_user_info(self, access_token):
        try:
            response = requests.get(self.USER_INFO_URL, params={"access_token": access_token})
            response_data = response.json()
            return response_data
        except Exception as e:
            return {"error": f"User info error: {str(e)}"}

    def create_or_get_user(self, user_info):
        try:
            email = user_info['email']
            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                user_data = {
                    'email': user_info['email'],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'username': user_info['email'],
                    'is_active': True,
                }
                user = CustomUser.objects.create(**user_data)

            return user
        except Exception as e:
            raise e

    def get_jwt_token(self, user):
        if not user.username:
            user.username = user.email
            user.save()
        
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return access_token, refresh_token
        except Exception as e:
            raise e


class FacebookLoginService:
    AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    USER_INFO_URL = "https://graph.facebook.com/v18.0/me"

    def get_authorization_url(self):
        params = {
            "client_id": settings.FACEBOOK_APP_ID,
            "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
            "response_type": "code",
            "scope": "email,public_profile",
        }
        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        return auth_url

    def get_tokens(self, code):
        data = {
            "code": code,
            "client_id": settings.FACEBOOK_APP_ID,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        }

        try:
            response = requests.get(self.TOKEN_URL, params=data)
            response_data = response.json()
            return response_data
        except Exception as e:
            return {"error": f"Token exchange error: {str(e)}"}

    def get_user_info(self, access_token):
        try:
            params = {
                "access_token": access_token,
                "fields": "id,name,email,first_name,last_name,picture"
            }
            response = requests.get(self.USER_INFO_URL, params=params)
            response_data = response.json()
            return response_data
        except Exception as e:
            return {"error": f"User info error: {str(e)}"}

    def create_or_get_user(self, user_info):
        try:
            email = user_info.get('email')
            if not email:
                raise ValueError("Email not provided by Facebook")
            
            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                user_data = {
                    'email': email,
                    'first_name': user_info.get('first_name', ''),
                    'last_name': user_info.get('last_name', ''),
                    'username': email,
                    'is_active': True,
                }
                user = CustomUser.objects.create(**user_data)

            return user
        except Exception as e:
            raise e

    def get_jwt_token(self, user):
        if not user.username:
            user.username = user.email
            user.save()
        
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return access_token, refresh_token
        except Exception as e:
            raise e
