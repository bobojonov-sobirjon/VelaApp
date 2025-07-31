from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.core.files.base import ContentFile
import os
import logging
from datetime import datetime

from apps.accounts.models import (
    CustomUserDetail, Rituals, RitualType, 
    MeditationGenerate, Plans, LikeMeditation, 
    UserCheckIn, MeditationLibrary, UserPlan
)

# Import local meditation generation functions
from apps.accounts.generate.functions import (
    sleep_function, spark_function, calm_function, 
    dream_function, check_in_function
)

# Set up logger
logger = logging.getLogger(__name__)

User = get_user_model()


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'placeholder': 'Enter password'})
    password_confirm = serializers.CharField(write_only=True, required=False,
                                             style={'placeholder': 'Enter password confirmation'})

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name',
                  'password', 'password_confirm', 'is_agree']

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        # If password is provided, password_confirm must also be provided and match
        if password or password_confirm:
            if not password:
                raise ValidationError({"password": "Password is required when password_confirm is provided"})
            if not password_confirm:
                raise ValidationError({"password_confirm": "Password confirmation is required when password is provided"})
            if password != password_confirm:
                raise ValidationError({"password_confirm": "Passwords do not match"})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)

        if not password:
            raise ValidationError({"password": "Password is required for user creation"})

        email = validated_data.pop('email')
        
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            **validated_data
        )

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance


class CustomAuthTokenSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'placeholder': 'Enter password'})

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            raise serializers.ValidationError("Телефон и пароль, оба поля обязательны")

        user_model = get_user_model()

        user = user_model.objects.filter(email=identifier).first()

        if user is None:
            raise AuthenticationFailed("Неверные данные, пользователь не найден")

        if not user.check_password(password):
            raise AuthenticationFailed("Неверные данные, неправильный пароль")

        # Record login for successful authentication
        from apps.accounts.models import UserLoginTracker
        UserLoginTracker.record_login(user)

        return {
            'user': user,
        }

class UserCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCheckIn
        fields = ['id','check_in_date', 'check_in_choice', 'description']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class CustomUserDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    weekly_login_stats = serializers.SerializerMethodField()
    check_in = UserCheckInSerializer(many=True, read_only=True)
    

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'first_name', 'last_name', 'avatar', 'weekly_login_stats', 'check_in'
        ]
    
    def get_weekly_login_stats(self, obj):
        """Get weekly login statistics for the user"""
        try:
            user_detail = obj.details.first()
            if user_detail:
                return user_detail.get_weekly_login_stats()
            return None
        except Exception:
            return None

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PasswordUpdateSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class PlanSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    
    def get_description(self, obj):
        # Get the first plan description or return empty string
        plan_description = obj.plan_description.first()
        return plan_description.description if plan_description else ""
    
    class Meta:
        model = Plans
        fields = ['id', 'name', 'price', 'is_monthly', 'is_annual', 'is_free_trial', 'discount', 'description']
        
    def create(self, validated_data):
        return super().create(validated_data)


class CombinedProfileSerializer(serializers.Serializer):
    # Plan Type fields
    plan_type = serializers.IntegerField(required=False)
    
    # User Detail fields
    gender = serializers.ChoiceField(choices=CustomUserDetail.GenderChoices.choices, required=False, allow_blank=True)
    dream = serializers.CharField(required=False, allow_blank=True)
    goals = serializers.CharField(required=False, allow_blank=True)
    age_range = serializers.CharField(max_length=20, required=False, allow_blank=True)
    happiness = serializers.CharField(required=False, allow_blank=True)
    
    # Ritual fields
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    ritual_type = serializers.ChoiceField(choices=Rituals.RitualTypeChoices.choices, required=False)
    tone = serializers.ChoiceField(choices=Rituals.ToneChoices.choices, required=False)
    voice = serializers.ChoiceField(choices=Rituals.VoiceChoices.choices, required=False)
    duration = serializers.ChoiceField(choices=Rituals.DurationChoices.choices, required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        
        # Check if user has a valid plan (free trial or paid)
        user_plans = UserPlan.objects.filter(user=user, is_active=True)
        
        # Check for active free trial (within 5 days)
        free_trial_plans = user_plans.filter(plan__is_free_trial=True)
        has_valid_free_trial = False
        
        for user_plan in free_trial_plans:
            days_since_creation = (timezone.now() - user_plan.created_at).days
            if days_since_creation <= 5:
                has_valid_free_trial = True
                break
        
        # Check for paid plans (monthly/annual)
        paid_plans = user_plans.filter(plan__is_free_trial=False)
        has_valid_paid_plan = False
        
        for user_plan in paid_plans:
            # For monthly plans - check if within 30 days
            if user_plan.plan.is_monthly:
                days_since_start = (timezone.now() - user_plan.start_date).days
                if days_since_start <= 30:
                    has_valid_paid_plan = True
                    break
            # For annual plans - check if within 365 days
            elif user_plan.plan.is_annual:
                days_since_start = (timezone.now() - user_plan.start_date).days
                if days_since_start <= 365:
                    has_valid_paid_plan = True
                    break
        
        if not (has_valid_free_trial or has_valid_paid_plan):
            # Check if user had free trial but it expired
            expired_free_trials = free_trial_plans.filter(
                created_at__lte=timezone.now() - timezone.timedelta(days=5)
            )
            
            if expired_free_trials.exists():
                raise serializers.ValidationError("Your free trial has expired. Please upgrade to a paid plan to continue using this feature.")
            else:
                raise serializers.ValidationError("You need to have a free trial or paid plan to use this feature")
        
        # Extract user detail fields
        
        # Extract user detail fields
        user_detail_fields = ['gender', 'dream', 'goals', 'age_range', 'happiness']
        user_detail_data = {k: v for k, v in validated_data.items() if k in user_detail_fields}
        
        # Extract ritual fields
        ritual_fields = ['name', 'description', 'ritual_type', 'tone', 'voice', 'duration']
        ritual_data = {k: v for k, v in validated_data.items() if k in ritual_fields}
        
        # Create or update user detail
        user_detail, created = CustomUserDetail.objects.get_or_create(user=user)
        for field, value in user_detail_data.items():
            setattr(user_detail, field, value)
        user_detail.save()
        
        # Create ritual if ritual data is provided
        ritual = None
        if any(ritual_data.values()):
            ritual = Rituals.objects.create(**ritual_data)
        
        try:
            plan_type = RitualType.objects.get(id=validated_data['plan_type'])
        except RitualType.DoesNotExist:
            raise serializers.ValidationError("Ritual type not found")
        
        # Generate meditation file
        meditation_file = self.generate_meditation(plan_type, ritual, user_detail)
        
        with transaction.atomic():
            meditation = MeditationGenerate.objects.create(
                user=user,
                details=ritual,
                ritual_type=plan_type,
                file=meditation_file
            )
        
        return {
            'user_detail': user_detail,
            'ritual': ritual
        }

    
    def generate_meditation(self, plan_type, ritual, user_detail):
        """
        Generate meditation file using local functions based on plan type
        """
        # Map plan types to their corresponding functions
        function_mapping = {
            "Sleep Manifestation": sleep_function,
            "Morning Spark": spark_function, 
            "Calming Reset": calm_function,
            "Dream Visualizer": dream_function
        }
        
        # Get the appropriate function
        generation_function = function_mapping.get(plan_type.name)
        if not generation_function:
            raise serializers.ValidationError(f"Unknown plan type: {plan_type.name}")
        
        # Prepare parameters for the function
        name = ritual.name or "Meditation"
        goals = user_detail.goals or ""
        dreamlife = user_detail.dream or ""
        dream_activities = user_detail.happiness or ""
        ritual_type = ritual.ritual_type or "Story"
        tone = ritual.tone or "Dreamy"
        voice = ritual.voice or "Female"
        length = int(ritual.duration) if ritual.duration else 2
        check_in = ""
        
        # Validate length parameter
        if length not in [2, 5, 10]:
            length = 2  # Default to 2 minutes if invalid
        
        # Validate ritual_type parameter
        if ritual_type not in ["Story", "Guided"]:
            ritual_type = "Story"
        
        # Validate tone parameter
        if tone not in ["Dreamy", "ASMR"]:
            tone = "Dreamy"
        
        # Validate voice parameter
        if voice not in ["Female", "Male"]:
            voice = "Female"
        
        		# Generate meditation with provided parameters
        
        try:
            # Call the appropriate function to generate audio
            audio_data = generation_function(
                name=name,
                goals=goals,
                dreamlife=dreamlife,
                dream_activities=dream_activities,
                ritual_type=ritual_type,
                tone=tone,
                voice=voice,
                length=length,
                check_in=check_in
            )
            
            # Create a filename for the meditation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meditation_{plan_type.name.lower().replace(' ', '_')}_{timestamp}.mp3"
            
            # Create ContentFile from audio data
            content_file = ContentFile(audio_data, name=filename)
            
            			# Meditation generated successfully
            
            return content_file
            
        except Exception as e:
            # Log the error and create a placeholder file
            			# Log error and create placeholder
            logger.error(f"Meditation generation failed: {str(e)}")
            return self._create_placeholder_file(plan_type, ritual)
    
    def _create_placeholder_file(self, plan_type, ritual):
        """
        Use a default MP3 file from muzic as the placeholder when external API is unavailable
        """
        # Path to the default MP3 file
        default_mp3_path = os.path.join(os.path.dirname(__file__), 'muzic', 'sleep_manifestation.mp3')
        
        # Generate a unique filename for the placeholder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meditation_{plan_type.name.lower().replace(' ', '_')}_{timestamp}.mp3"

        try:
            with open(default_mp3_path, 'rb') as f:
                audio_data = f.read()
            content_file = ContentFile(audio_data, name=filename)
            return content_file
        except Exception as e:
            logger.error(f"Failed to load default placeholder MP3: {str(e)}")
            # Fallback: return a minimal ContentFile with error message
            content = f"Placeholder audio unavailable. Error: {str(e)}"
            return ContentFile(content.encode('utf-8'), name=filename)
    

class RitualsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rituals
        fields = ['id', 'name', 'description', 'ritual_type', 'tone', 'voice', 'duration']
        

class RitualTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualType
        fields = ['id', 'name', 'description']
    

class MeditationGenerateListSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    ritual_type = serializers.SerializerMethodField()

    class Meta:
        model = MeditationGenerate
        fields = ['id', 'details', 'ritual_type', 'file', 'created_at']

    def get_is_deleted_false(self, obj):
        return obj.is_deleted == False

    def get_is_deleted_true(self, obj):
        return obj.is_deleted == True
    
    def get_details(self, obj):
        return RitualsSerializer(obj.details).data
    
    def get_ritual_type(self, obj):
        return RitualTypeSerializer(obj.ritual_type).data


class MeditationLibraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationLibrary
        fields = ['id', 'name', 'image', 'description', 'file', 'created_at']
    

class RitualTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualType
        fields = ['id', 'name', 'description']