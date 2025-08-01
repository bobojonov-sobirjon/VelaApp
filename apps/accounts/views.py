import requests
import json
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings

from urllib.parse import urlparse, parse_qs

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from django.utils import timezone

from apps.accounts.serializers import (
	SignUpSerializer, CustomAuthTokenSerializer, CustomUserDetailSerializer,
	PasswordUpdateSerializer, PlanSerializer, CombinedProfileSerializer,
	UserCheckInSerializer, MeditationGenerateListSerializer, MeditationLibraryListSerializer, RitualTypeListSerializer,
	UserLifeVisionSerializer, UserLifeVisionListSerializer, UserLifeVisionCreateSerializer, UserLifeVisionUpdateSerializer,
	ExternalMeditationSerializer
)
from apps.accounts.services import GoogleLoginService, FacebookLoginService, ExternalMeditationService
from apps.accounts.models import LikeMeditation, Plans, MeditationGenerate, MeditationLibrary, UserPlan, UserLifeVision

User = get_user_model()

# Set up logger
logger = logging.getLogger(__name__)


class GoogleLoginAPIView(APIView):
	permission_classes = [AllowAny]

	@swagger_auto_schema(
		operation_summary="Google OAuth2 Authentication URL",
		operation_description="This endpoint returns the URL to begin the Google OAuth2 authentication process.",
		tags=['Authentication'],
		responses={
			200: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"auth_url": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="URL to authenticate via Google OAuth2."
					),
				}
			),
		}
	)
	def get(self, request):
		"""Get Google OAuth2 authentication URL"""
		google_service = GoogleLoginService()
		auth_url = google_service.get_authorization_url()
		return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)

	@swagger_auto_schema(
		operation_summary="Exchange Code for JWT Tokens",
		operation_description="This endpoint exchanges the Google OAuth2 authorization code for JWT access and refresh tokens.",
		tags=['Authentication'],
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			properties={
				"code": openapi.Schema(
					type=openapi.TYPE_STRING,
					description="The authorization code from Google OAuth2."
				),
			},
			required=["code"]
		),
		responses={
			200: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"access_token": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="JWT access token."
					),
					"refresh_token": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="JWT refresh token."
					),
				}
			),
			400: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"error": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="Description of the error."
					),
				}
			),
		}
	)
	def post(self, request):
		"""Exchange Google OAuth2 code for JWT tokens"""
		code = request.data.get('code')

		if not code:
			return Response({"error": "Authorization code missing"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			google_service = GoogleLoginService()

			tokens = google_service.get_tokens(code)

			if 'error' in tokens or 'access_token' not in tokens:
				error_msg = tokens.get('error', 'Failed to retrieve tokens')
				error_description = tokens.get('error_description', '')

				if error_msg == "invalid_grant":
					detailed_error = "Invalid authorization code. Possible reasons:\n"
					detailed_error += "1. Code already used\n2. Code expired\n3. Redirect URI mismatch\n4. Clock issue\n"
					detailed_error += f"Original error: {error_msg}"
					if error_description:
						detailed_error += f" - {error_description}"

					return Response({
						"error": detailed_error,
						"debug_info": {
							"client_id": settings.GOOGLE_CLIENT_ID[:20] + "...",
							"redirect_uri": settings.GOOGLE_REDIRECT_URI,
							"code_length": len(code),
							"original_error": error_msg,
							"error_description": error_description
						}
					}, status=status.HTTP_400_BAD_REQUEST)

				return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

			user_info = google_service.get_user_info(tokens['access_token'])

			if 'error' in user_info:
				return Response({"error": user_info['error']}, status=status.HTTP_400_BAD_REQUEST)

			user = google_service.create_or_get_user(user_info)

			try:
				access_token, refresh_token = google_service.get_jwt_token(user)
				return Response({
					"access_token": access_token,
					"refresh_token": refresh_token
				}, status=status.HTTP_200_OK)

			except Exception as jwt_error:
				raise jwt_error

		except ValueError as e:
			return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FacebookLoginAPIView(APIView):
	permission_classes = [AllowAny]

	@swagger_auto_schema(
		operation_summary="Facebook OAuth2 Authentication URL",
		operation_description="This endpoint returns the URL to begin the Facebook OAuth2 authentication process.",
		tags=['Authentication'],
		responses={
			200: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"auth_url": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="URL to authenticate via Facebook OAuth2."
					),
				}
			),
		}
	)
	def get(self, request):
		"""Get Facebook OAuth2 authentication URL"""
		facebook_service = FacebookLoginService()
		auth_url = facebook_service.get_authorization_url()
		return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)

	@swagger_auto_schema(
		operation_summary="Exchange Code for JWT Tokens",
		operation_description="This endpoint exchanges the Facebook OAuth2 authorization code for JWT access and refresh tokens.",
		tags=['Authentication'],
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			properties={
				"code": openapi.Schema(
					type=openapi.TYPE_STRING,
					description="The authorization code from Facebook OAuth2."
				),
			},
			required=["code"]
		),
		responses={
			200: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"access_token": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="JWT access token."
					),
					"refresh_token": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="JWT refresh token."
					),
				}
			),
			400: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"error": openapi.Schema(
						type=openapi.TYPE_STRING,
						description="Description of the error."
					),
				}
			),
		}
	)
	def post(self, request):
		"""Exchange Facebook OAuth2 code for JWT tokens"""
		code = request.data.get('code')

		if not code:
			return Response({"error": "Authorization code missing"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			facebook_service = FacebookLoginService()

			tokens = facebook_service.get_tokens(code)

			if 'error' in tokens or 'access_token' not in tokens:
				error_msg = tokens.get('error', 'Failed to retrieve tokens')
				error_description = tokens.get('error_description', '')

				if 'invalid_grant' in error_msg or 'authorization_expired' in error_msg:
					detailed_error = "Invalid authorization code. Possible reasons:\n"
					detailed_error += "1. Code already used\n2. Code expired\n3. Redirect URI mismatch\n4. App configuration issue\n"
					detailed_error += f"Original error: {error_msg}"
					if error_description:
						detailed_error += f" - {error_description}"

					return Response({
						"error": detailed_error,
						"debug_info": {
							"app_id": settings.FACEBOOK_APP_ID[:10] + "...",
							"redirect_uri": settings.FACEBOOK_REDIRECT_URI,
							"code_length": len(code),
							"original_error": error_msg,
							"error_description": error_description
						}
					}, status=status.HTTP_400_BAD_REQUEST)

				return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

			user_info = facebook_service.get_user_info(tokens['access_token'])

			if 'error' in user_info:
				return Response({"error": user_info['error']}, status=status.HTTP_400_BAD_REQUEST)

			user = facebook_service.create_or_get_user(user_info)

			try:
				access_token, refresh_token = facebook_service.get_jwt_token(user)
				return Response({
					"access_token": access_token,
					"refresh_token": refresh_token
				}, status=status.HTTP_200_OK)

			except Exception as jwt_error:
				raise jwt_error

		except ValueError as e:
			return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSignupView(APIView):
	permission_classes = [AllowAny]

	@swagger_auto_schema(request_body=SignUpSerializer, tags=['Account'])
	def post(self, request, *args, **kwargs):
		serializer = SignUpSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthTokenView(APIView):
	permission_classes = [AllowAny]

	@swagger_auto_schema(request_body=CustomAuthTokenSerializer, tags=['Account'])
	def post(self, request):
		serializer = CustomAuthTokenSerializer(data=request.data)

		if serializer.is_valid():
			user = serializer.validated_data['user']
			refresh = RefreshToken.for_user(user)

			return Response({
				'refresh': str(refresh),
				'access': str(refresh.access_token),
			}, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserDetailView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: CustomUserDetailSerializer()},
		operation_description="Retrieve details of the authenticated user.", tags=['Account']
	)
	def get(self, request):
		user = request.user
		serializer = CustomUserDetailSerializer(user, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)

	@swagger_auto_schema(
		responses={200: CustomUserDetailSerializer()},
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			properties={
				'first_name': openapi.Schema(type=openapi.TYPE_STRING, max_length=30),
				'last_name': openapi.Schema(type=openapi.TYPE_STRING, max_length=30),
				'avatar': openapi.Schema(type=openapi.TYPE_FILE, description='User avatar image'),
			}
		),
		operation_description="Update the authenticated user's profile. Supports both JSON and multipart/form-data for avatar uploads.",
		tags=['Account']
	)
	def put(self, request):
		user = request.user
		serializer = CustomUserDetailSerializer(user, data=request.data, partial=True, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={204: 'No Content'},
		operation_description="Delete the authenticated user's account.", tags=['Account']
	)
	def delete(self, request):
		user = request.user
		user.delete()
		return Response({"detail": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CustomUserView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: CustomUserDetailSerializer()},
		operation_description="Retrieve details of the guest user.", tags=['Account']
	)
	def get(self, request, *args, **kwargs):
		user_model = get_user_model()
		user = get_object_or_404(user_model, id=kwargs.get('id'))
		serializer = CustomUserDetailSerializer(user, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordUpdateView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		request_body=PasswordUpdateSerializer,
		tags=['Account'],
		responses={
			200: "Password updated successfully.",
			400: "Bad Request: Password update failed."
		},
		operation_description="Update the authenticated user's password."
	)
	def patch(self, request):
		serializer = PasswordUpdateSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.update(request.user, serializer.validated_data)
			return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanListView(APIView):
	permission_classes = [AllowAny]

	@swagger_auto_schema(
		tags=['Plans'],
		responses={200: PlanSerializer(many=True)},
		operation_description="Retrieve all plans.",
	)
	def get(self, request):
		plans = Plans.objects.all()
		serializer = PlanSerializer(plans, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)

	@swagger_auto_schema(
		tags=['Plans'],
		request_body=PlanSerializer,
		responses={201: PlanSerializer()},
		operation_description="Create a new plan.",
	)
	def post(self, request):
		serializer = PlanSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CombinedProfileView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		request_body=CombinedProfileSerializer,
		responses={
			201: openapi.Schema(
				type=openapi.TYPE_OBJECT,
				properties={
					"user_detail": openapi.Schema(type=openapi.TYPE_OBJECT),
					"ritual": openapi.Schema(type=openapi.TYPE_OBJECT),
					"meditation": openapi.Schema(type=openapi.TYPE_OBJECT),
					"file_url": openapi.Schema(type=openapi.TYPE_STRING, description="URL to the generated meditation file"),
				}
			),
			400: "Bad Request: Validation error"
		},
		operation_description="Create or update user profile and generate meditation based on plan type.",
		tags=['Profile']
	)
	def post(self, request):
		serializer = CombinedProfileSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			try:
				result = serializer.save()
				
				# Get the latest meditation file for this user
				latest_meditation = MeditationGenerate.objects.filter(
					user=request.user
				).order_by('-created_at').first()
				
				# Build response with file URL
				response_data = {
					"message": "Profile updated and meditation generated successfully",
					"user_detail": {
						"id": result['user_detail'].id,
						"dream": result['user_detail'].dream,
						"goals": result['user_detail'].goals,
						"age_range": result['user_detail'].age_range,
						"gender": result['user_detail'].gender,
						"happiness": result['user_detail'].happiness,
					},
					"ritual": {
						"id": result['ritual'].id if result['ritual'] else None,
						"name": result['ritual'].name if result['ritual'] else None,
						"description": result['ritual'].description if result['ritual'] else None,
						"ritual_type": result['ritual'].ritual_type if result['ritual'] else None,
						"tone": result['ritual'].tone if result['ritual'] else None,
						"voice": result['ritual'].voice if result['ritual'] else None,
						"duration": result['ritual'].duration if result['ritual'] else None,
					} if result['ritual'] else None
				}
				
				# Return response with file URL if meditation was generated
				if latest_meditation and latest_meditation.file:
					response_data["file_url"] = request.build_absolute_uri(latest_meditation.file.url)
				
				return Response(response_data, status=status.HTTP_201_CREATED)
			except Exception as e:
				return Response({
					"error": f"Failed to process request: {str(e)}"
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeMeditationView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		operation_description="Like a meditation.",
		tags=['Like Meditation'],
		responses={200: "Meditation liked successfully."},
	)
	def get(self, request, *args, **kwargs):
		meditation_id = kwargs.get('id')
		meditation = get_object_or_404(MeditationGenerate, id=meditation_id)
		like_meditation = LikeMeditation.objects.filter(user=request.user, meditation=meditation).first()
		
		if not like_meditation:
			LikeMeditation.objects.create(user=request.user, meditation=meditation)
			return Response({"message": "Meditation liked successfully."}, status=status.HTTP_200_OK)
		else:
			return Response({"message": "Meditation already liked."}, status=status.HTTP_400_BAD_REQUEST)
	

class UnlikeMeditationView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		operation_description="Unlike a meditation.",
		tags=['Unlike Meditation'],
		responses={200: "Meditation unliked successfully."},
	)
	def get(self, request, *args, **kwargs):
		meditation_id = kwargs.get('id')
		meditation = get_object_or_404(MeditationGenerate, id=meditation_id)
		like_meditation = LikeMeditation.objects.filter(user=request.user, meditation=meditation).first()
		
		if like_meditation:
			like_meditation.delete()
			return Response({"message": "Meditation unliked successfully."}, status=status.HTTP_200_OK)
		else:
			return Response({"message": "Meditation not liked."}, status=status.HTTP_400_BAD_REQUEST)


class UserCheckInView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		request_body=UserCheckInSerializer,
		responses={201: UserCheckInSerializer()},
		operation_description="Create a new check-in.",
		tags=['Check In']
	)
	def post(self, request):
		serializer = UserCheckInSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

class MyMeditationView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: MeditationGenerateListSerializer(many=True)},
		operation_description="Get all meditations for the authenticated user.",
		tags=['My Meditations']
	)
	def get(self, request):
		meditations = MeditationGenerate.objects.filter(user=request.user, is_deleted=False)
		serializer = MeditationGenerateListSerializer(meditations, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	
class MeditationLibraryView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: MeditationLibraryListSerializer(many=True)},
		operation_description="Get all meditations for the authenticated user.",
		tags=['Meditation Library']
	)
	def get(self, request):
		meditations = MeditationLibrary.objects.all()
		serializer = MeditationLibraryListSerializer(meditations, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteMeditationView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: "Meditation deleted successfully."},
		operation_description="Delete a meditation.",
		tags=['Meditation Library']
	)
	def delete(self, request, *args, **kwargs):
		meditation_id = kwargs.get('id')
		meditation = get_object_or_404(MeditationGenerate, id=meditation_id)
		meditation.is_deleted = True
		meditation.save()
		return Response({"message": "Meditation deleted successfully."}, status=status.HTTP_200_OK)


class RestoreMeditationView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: "Meditation restored successfully."},
		operation_description="Restore a meditation.",
		tags=['Meditation Library']
	)
	def get(self, request, *args, **kwargs):
		meditations = MeditationGenerate.objects.all().filter(is_deleted=True)
		serializer = MeditationGenerateListSerializer(meditations, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class AssignFreeTrialView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={
			200: "Free trial assigned successfully.",
			400: "Free trial already assigned or error occurred."
		},
		operation_description="Assign a free trial plan to the authenticated user.",
		tags=['Plans']
	)
	def post(self, request):
		user = request.user
		
		# Check if user already has an active plan
		active_plans = UserPlan.objects.filter(user=user, is_active=True)
		
		# Check for expired free trials and deactivate them
		expired_free_trials = active_plans.filter(
			plan__is_free_trial=True,
			created_at__lte=timezone.now() - timezone.timedelta(days=5)
		)
		for expired_plan in expired_free_trials:
			expired_plan.is_active = False
			expired_plan.save()
		
		# Check if user has any valid active plans
		valid_plans = UserPlan.objects.filter(user=user, is_active=True)
		has_valid_plan = False
		
		for user_plan in valid_plans:
			if user_plan.plan.is_free_trial:
				# Check if free trial is within 5 days
				days_since_creation = (timezone.now() - user_plan.created_at).days
				if days_since_creation <= 5:
					has_valid_plan = True
					break
			else:
				# Check if paid plan is within its period
				if user_plan.plan.is_monthly:
					days_since_start = (timezone.now() - user_plan.start_date).days
					if days_since_start <= 30:
						has_valid_plan = True
						break
				elif user_plan.plan.is_annual:
					days_since_start = (timezone.now() - user_plan.start_date).days
					if days_since_start <= 365:
						has_valid_plan = True
						break
		
		if has_valid_plan:
			return Response(
				{"error": "User already has an active plan"}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		# Get or create a free trial plan
		free_trial_plan, created = Plans.objects.get_or_create(
			is_free_trial=True,
			defaults={
				'name': 'Free Trial',
				'price': 0.00,
				'is_monthly': True,
				'is_annual': False,
				'discount': 0.00
			}
		)
		
		# Assign the free trial to the user
		user_plan, created = UserPlan.objects.get_or_create(
			user=user,
			plan=free_trial_plan,
			defaults={'is_active': True}
		)
		
		return Response(
			{"message": "Free trial assigned successfully", "plan": free_trial_plan.name}, 
			status=status.HTTP_200_OK
		)


class CheckPlanStatusView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={
			200: "Plan status information.",
		},
		operation_description="Check the current plan status of the authenticated user.",
		tags=['Plans']
	)
	def get(self, request):
		user = request.user
		user_plans = UserPlan.objects.filter(user=user, is_active=True)
		
		plan_status = {
			"has_active_plan": False,
			"plan_type": None,
			"days_remaining": 0,
			"plan_name": None,
			"message": None
		}
		
		for user_plan in user_plans:
			if user_plan.plan.is_free_trial:
				days_since_creation = (timezone.now() - user_plan.created_at).days
				days_remaining = max(0, 5 - days_since_creation)
				
				if days_remaining > 0:
					plan_status.update({
						"has_active_plan": True,
						"plan_type": "free_trial",
						"days_remaining": days_remaining,
						"plan_name": user_plan.plan.name,
						"message": f"Free trial active. {days_remaining} days remaining."
					})
				else:
					plan_status.update({
						"has_active_plan": False,
						"plan_type": "expired_free_trial",
						"days_remaining": 0,
						"plan_name": user_plan.plan.name,
						"message": "Free trial expired. Please upgrade to a paid plan."
					})
					# Deactivate expired free trial
					user_plan.is_active = False
					user_plan.save()
				break
			else:
				# Paid plan
				if user_plan.plan.is_monthly:
					days_since_start = (timezone.now() - user_plan.start_date).days
					days_remaining = max(0, 30 - days_since_start)
					plan_type = "monthly"
				elif user_plan.plan.is_annual:
					days_since_start = (timezone.now() - user_plan.start_date).days
					days_remaining = max(0, 365 - days_since_start)
					plan_type = "annual"
				else:
					continue
				
				if days_remaining > 0:
					plan_status.update({
						"has_active_plan": True,
						"plan_type": plan_type,
						"days_remaining": days_remaining,
						"plan_name": user_plan.plan.name,
						"message": f"Paid plan active. {days_remaining} days remaining."
					})
				else:
					plan_status.update({
						"has_active_plan": False,
						"plan_type": f"expired_{plan_type}",
						"days_remaining": 0,
						"plan_name": user_plan.plan.name,
						"message": "Paid plan expired. Please renew your subscription."
					})
					# Deactivate expired paid plan
					user_plan.is_active = False
					user_plan.save()
				break
		
		if not plan_status["has_active_plan"] and not plan_status["plan_type"]:
			plan_status["message"] = "No active plan found. Please get a free trial or purchase a plan."
		
		return Response(plan_status, status=status.HTTP_200_OK)


class CountMeditationView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		responses={200: "Count of meditations."},
		operation_description="Count the number of meditations for the authenticated user.",
		tags=['Meditation Library']
	)
	def get(self, request):
		user = request.user
		meditations = MeditationGenerate.objects.filter(user=user, is_deleted=False)
		count = meditations.count()
		archive_meditations = MeditationGenerate.objects.filter(user=user, is_deleted=True)		
		archive_count = archive_meditations.count()
		return Response({"count": count, "archive_count": archive_count}, status=status.HTTP_200_OK)


class RitualTypeView(APIView):
	permission_classes = [AllowAny]

	@swagger_auto_schema(
		responses={200: RitualTypeListSerializer(many=True)},
		operation_description="Get all ritual types.",
		tags=['Ritual Types']
	)
	def get(self, request):
		ritual_types = RitualType.objects.all()
		serializer = RitualTypeListSerializer(ritual_types, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class UserLifeVisionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get all life visions for authenticated user",
        operation_description="Retrieve all life visions, goals, and dreams for the authenticated user",
        tags=['Life Vision'],
        responses={
            200: UserLifeVisionListSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def get(self, request):
        """Get all life visions for the authenticated user"""
        visions = UserLifeVision.objects.filter(user=request.user, is_active=True)
        
        # Filter by vision type if provided
        vision_type = request.query_params.get('vision_type')
        if vision_type:
            visions = visions.filter(vision_type=vision_type)
        
        # Filter by goal status if provided
        goal_status = request.query_params.get('goal_status')
        if goal_status:
            visions = visions.filter(goal_status=goal_status)
        
        serializer = UserLifeVisionListSerializer(visions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLifeVisionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Create a new life vision",
        operation_description="Create a new life vision, goal, or dream for the authenticated user",
        request_body=UserLifeVisionCreateSerializer,
        tags=['Life Vision'],
        responses={
            201: UserLifeVisionSerializer(),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def post(self, request):
        """Create a new life vision"""
        serializer = UserLifeVisionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            vision = serializer.save()
            response_serializer = UserLifeVisionSerializer(vision)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLifeVisionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get specific life vision details",
        operation_description="Retrieve details of a specific life vision",
        tags=['Life Vision'],
        responses={
            200: UserLifeVisionSerializer(),
            404: "Not Found",
            401: "Unauthorized"
        }
    )
    def get(self, request, vision_id):
        """Get specific life vision details"""
        try:
            vision = UserLifeVision.objects.get(id=vision_id, user=request.user)
            serializer = UserLifeVisionSerializer(vision)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserLifeVision.DoesNotExist:
            return Response({"error": "Life vision not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_summary="Update a life vision",
        operation_description="Update an existing life vision",
        request_body=UserLifeVisionUpdateSerializer,
        tags=['Life Vision'],
        responses={
            200: UserLifeVisionSerializer(),
            400: "Bad Request",
            404: "Not Found",
            401: "Unauthorized"
        }
    )
    def put(self, request, vision_id):
        """Update a life vision"""
        try:
            vision = UserLifeVision.objects.get(id=vision_id, user=request.user)
            serializer = UserLifeVisionUpdateSerializer(vision, data=request.data, partial=True)
            if serializer.is_valid():
                updated_vision = serializer.save()
                response_serializer = UserLifeVisionSerializer(updated_vision)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserLifeVision.DoesNotExist:
            return Response({"error": "Life vision not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_summary="Delete a life vision",
        operation_description="Soft delete a life vision (marks as inactive)",
        tags=['Life Vision'],
        responses={
            204: "No Content",
            404: "Not Found",
            401: "Unauthorized"
        }
    )
    def delete(self, request, vision_id):
        """Delete a life vision (soft delete)"""
        try:
            vision = UserLifeVision.objects.get(id=vision_id, user=request.user)
            vision.is_active = False
            vision.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserLifeVision.DoesNotExist:
            return Response({"error": "Life vision not found"}, status=status.HTTP_404_NOT_FOUND)


class UserLifeVisionCompleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Mark a life vision as completed",
        operation_description="Mark a specific life vision or goal as completed",
        tags=['Life Vision'],
        responses={
            200: UserLifeVisionSerializer(),
            404: "Not Found",
            401: "Unauthorized"
        }
    )
    def post(self, request, vision_id):
        """Mark a life vision as completed"""
        try:
            vision = UserLifeVision.objects.get(id=vision_id, user=request.user)
            vision.mark_as_completed()
            serializer = UserLifeVisionSerializer(vision)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserLifeVision.DoesNotExist:
            return Response({"error": "Life vision not found"}, status=status.HTTP_404_NOT_FOUND)


class UserLifeVisionStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get life vision statistics",
        operation_description="Get statistics about user's life visions, goals, and dreams",
        tags=['Life Vision'],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_visions': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'completed_goals': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'in_progress_goals': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'not_started_goals': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'vision_type_breakdown': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            401: "Unauthorized"
        }
    )
    def get(self, request):
        """Get life vision statistics for the authenticated user"""
        visions = UserLifeVision.objects.filter(user=request.user, is_active=True)
        
        total_visions = visions.count()
        completed_goals = visions.filter(is_completed=True).count()
        in_progress_goals = visions.filter(goal_status=UserLifeVision.GoalStatusChoices.IN_PROGRESS).count()
        not_started_goals = visions.filter(goal_status=UserLifeVision.GoalStatusChoices.NOT_STARTED).count()
        
        completion_rate = (completed_goals / total_visions * 100) if total_visions > 0 else 0
        
        # Vision type breakdown
        vision_type_breakdown = {}
        for vision_type, _ in UserLifeVision.VisionTypeChoices.choices:
            count = visions.filter(vision_type=vision_type).count()
            vision_type_breakdown[vision_type] = count
        
        stats = {
            'total_visions': total_visions,
            'completed_goals': completed_goals,
            'in_progress_goals': in_progress_goals,
            'not_started_goals': not_started_goals,
            'completion_rate': round(completion_rate, 2),
            'vision_type_breakdown': vision_type_breakdown,
        }
        
        return Response(stats, status=status.HTTP_200_OK)


class ExternalMeditationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=ExternalMeditationSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "plan_type": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the plan type used"),
                    "api_response": openapi.Schema(type=openapi.TYPE_OBJECT),
                    "endpoint_used": openapi.Schema(type=openapi.TYPE_STRING),
                    "file_url": openapi.Schema(type=openapi.TYPE_STRING, description="URL to the saved meditation file"),
                    "meditation_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the saved meditation record")
                }
            ),
            400: "Bad Request: Invalid plan type or missing required fields",
            500: "Internal Server Error: API request failed"
        },
        operation_description="Send meditation request to external API based on plan type ID. The plan_type field should be a valid RitualType ID that exists in the database. For choice fields, send keys instead of values: ritual_type ('story', 'guided_meditations'), tone ('dreamy', 'asmr'), voice ('male', 'female'), duration ('2', '5', '10'). The response includes the plan type name, saved file URL and meditation record ID.",
        tags=['External Meditation API']
    )
    def post(self, request):
        """
        Send meditation request to external API based on plan type
        """
        try:
            # Validate input data using serializer
            serializer = ExternalMeditationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    "error": "Validation failed",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process the meditation request using the service
            meditation_service = ExternalMeditationService()
            result = meditation_service.process_meditation_request(
                user=request.user,
                validated_data=serializer.validated_data
            )
            
            # Return the result - always return 200 if we have a meditation_id (successful creation)
            if result.get("meditation_id"):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in ExternalMeditationAPIView: {str(e)}")
            return Response({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeditationGenerateDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get meditation by ID",
        operation_description="Retrieve a specific meditation record by its ID. Only returns meditations belonging to the authenticated user.",
        tags=['Meditation'],
        responses={
            200: MeditationGenerateListSerializer(),
            404: "Meditation not found",
            401: "Unauthorized"
        }
    )
    def get(self, request, meditation_id):
        """
        Get a specific meditation record by ID
        """
        try:
            # Get the meditation record, ensuring it belongs to the authenticated user
            meditation = get_object_or_404(
                MeditationGenerate, 
                id=meditation_id, 
                user=request.user
            )
            
            # Serialize the meditation record
            serializer = MeditationGenerateListSerializer(meditation)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except MeditationGenerate.DoesNotExist:
            return Response({
                "error": "Meditation not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving meditation {meditation_id}: {str(e)}")
            return Response({
                "error": "An error occurred while retrieving the meditation"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)