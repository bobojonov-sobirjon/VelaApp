from django.urls import path

from apps.accounts.views import (
	UserSignupView,
	CustomAuthTokenView,
	CustomUserDetailView,
	CustomUserView,
	PasswordUpdateView, GoogleLoginAPIView,
	FacebookLoginAPIView,
	PlanListView,
	CombinedProfileView,
	LikeMeditationView,
	UnlikeMeditationView,
	UserCheckInView,
	MyMeditationView,
	MeditationLibraryView,
	DeleteMeditationView,
	RestoreMeditationView,
	AssignFreeTrialView,
	CheckPlanStatusView,
	CountMeditationView,
	RitualTypeView,
	UserLifeVisionListView,
	UserLifeVisionCreateView,
	UserLifeVisionDetailView,
	UserLifeVisionCompleteView,
	UserLifeVisionStatsView,
	ExternalMeditationAPIView,
	MeditationGenerateDetailView,
)

urlpatterns = [
	path('google/login/', GoogleLoginAPIView.as_view(), name='google_login'),
	path('facebook/login/', FacebookLoginAPIView.as_view(), name='facebook_login'),
	path('signup/', UserSignupView.as_view(), name='signup'),
	path('signin/', CustomAuthTokenView.as_view(), name='signin'),
	path('user-detail/', CustomUserDetailView.as_view(), name='user-detail'),
	path('user/<int:id>/', CustomUserView.as_view(), name='user-by-id'),
	path('update-password/', PasswordUpdateView.as_view(), name='update-password'),
	path('plans/', PlanListView.as_view(), name='plans'),
	
	# Combined Profile API
	path('meditation/combined/', CombinedProfileView.as_view(), name='combined-profile'),
	
	# External Meditation API
	path('meditation/external/', ExternalMeditationAPIView.as_view(), name='external-meditation'),
	
	# Meditation Detail API
	path('meditation/<int:meditation_id>/', MeditationGenerateDetailView.as_view(), name='meditation-detail'),
 
	# Like Meditation API
	path('like-meditation/<int:id>/', LikeMeditationView.as_view(), name='like-meditation'),
	path('unlike-meditation/<int:id>/', UnlikeMeditationView.as_view(), name='unlike-meditation'),
 
	# User Check In API
	path('check-in/', UserCheckInView.as_view(), name='check-in'),
 
	# My Meditations API
	path('my-meditations/', MyMeditationView.as_view(), name='my-meditations'),
 
	# Meditation Library API
	path('meditation-library/', MeditationLibraryView.as_view(), name='meditation-library'),
 
	# Delete Meditation API
	path('delete-meditation/<int:id>/', DeleteMeditationView.as_view(), name='delete-meditation'),
 
	# Restore Meditation API
	path('restore-meditation/', RestoreMeditationView.as_view(), name='restore-meditation'),
	
	# Assign Free Trial API
	path('assign-free-trial/', AssignFreeTrialView.as_view(), name='assign-free-trial'),
	
	# Check Plan Status API
	path('check-plan-status/', CheckPlanStatusView.as_view(), name='check-plan-status'),
 
	# Count Meditations API
	path('count-meditations/', CountMeditationView.as_view(), name='count-meditations'),
 
	# Ritual Type API
	path('ritual-types/', RitualTypeView.as_view(), name='ritual-types'),
	
	# Life Vision API - Separated endpoints
	path('life-vision/', UserLifeVisionListView.as_view(), name='life-vision-list'),  # GET - List all visions
	path('life-vision/create/', UserLifeVisionCreateView.as_view(), name='life-vision-create'),  # POST - Create new vision
	path('life-vision/<int:vision_id>/', UserLifeVisionDetailView.as_view(), name='life-vision-detail'),  # GET, PUT, DELETE - Single vision operations
	path('life-vision/<int:vision_id>/complete/', UserLifeVisionCompleteView.as_view(), name='life-vision-complete'),  # POST - Mark as completed
	path('life-vision/stats/', UserLifeVisionStatsView.as_view(), name='life-vision-stats'),  # GET - Statistics
]