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
    UserCheckIn, MeditationLibrary, UserPlan, UserLifeVision
)

# Import local meditation generation functions
from apps.accounts.generate.functions import (
    sleep_function, spark_function, calm_function, 
    dream_function, check_in_function
)

# Import custom exceptions
from config.exceptions import (
    PlanTypeNotFoundError, AuthenticationRequiredError, 
    SubscriptionRequiredError, TrialExpiredError, 
    MeditationGenerationError
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
        """Get weekly login status as array of day objects"""
        try:
            user_detail = obj.details.first()
            if user_detail:
                weekly_stats = user_detail.get_weekly_login_stats()
                days = weekly_stats.get('days', {})
                
                return [
                    {
                        "name": "Monday",
                        "login": days.get('Monday', {}).get('logged_in', False)
                    },
                    {
                        "name": "Tuesday",
                        "login": days.get('Tuesday', {}).get('logged_in', False)
                    },
                    {
                        "name": "Wednesday",
                        "login": days.get('Wednesday', {}).get('logged_in', False)
                    },
                    {
                        "name": "Thursday",
                        "login": days.get('Thursday', {}).get('logged_in', False)
                    },
                    {
                        "name": "Friday",
                        "login": days.get('Friday', {}).get('logged_in', False)
                    },
                    {
                        "name": "Saturday",
                        "login": days.get('Saturday', {}).get('logged_in', False)
                    },
                    {
                        "name": "Sunday",
                        "login": days.get('Sunday', {}).get('logged_in', False)
                    }
                ]
            
            # Default array if no user detail exists
            return [
                {"name": "Monday", "login": False},
                {"name": "Tuesday", "login": False},
                {"name": "Wednesday", "login": False},
                {"name": "Thursday", "login": False},
                {"name": "Friday", "login": False},
                {"name": "Saturday", "login": False},
                {"name": "Sunday", "login": False}
            ]
        except Exception:
            # Default array if error occurs
            return [
                {"name": "Monday", "login": False},
                {"name": "Tuesday", "login": False},
                {"name": "Wednesday", "login": False},
                {"name": "Thursday", "login": False},
                {"name": "Friday", "login": False},
                {"name": "Saturday", "login": False},
                {"name": "Sunday", "login": False}
            ]

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

    def validate(self, data):
        """
        Validate the input data before processing
        """
        # Check if plan_type is provided
        if 'plan_type' not in data or data['plan_type'] is None:
            raise serializers.ValidationError({
                'plan_type': 'Plan type is required to generate meditation.'
            }, code='missing_plan_type')
        
        # Validate plan_type exists
        try:
            plan_type = RitualType.objects.get(id=data['plan_type'])
        except RitualType.DoesNotExist:
            raise PlanTypeNotFoundError(f'Plan type with ID {data["plan_type"]} does not exist.')
        
        return data

    def create(self, validated_data):
        """
        Create meditation with proper error handling and status codes
        """
        user = self.context['request'].user
        
        # Validate user authentication
        if not user.is_authenticated:
            raise AuthenticationRequiredError('User must be authenticated to create meditation.')
        
        try:
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
                    raise TrialExpiredError('Your free trial has expired. Please upgrade to a paid plan to continue using this feature.')
                else:
                    raise SubscriptionRequiredError('You need to have a free trial or paid plan to use this feature.')
            
            # Extract user detail fields
            user_detail_fields = ['gender', 'dream', 'goals', 'age_range', 'happiness']
            user_detail_data = {k: v for k, v in validated_data.items() if k in user_detail_fields and v}
            
            # Extract ritual fields
            ritual_fields = ['name', 'description', 'ritual_type', 'tone', 'voice', 'duration']
            ritual_data = {k: v for k, v in validated_data.items() if k in ritual_fields and v}
            
            # Create or update user detail
            user_detail, created = CustomUserDetail.objects.get_or_create(user=user)
            for field, value in user_detail_data.items():
                setattr(user_detail, field, value)
            user_detail.save()
            
            # Create ritual if ritual data is provided
            ritual = None
            if ritual_data:
                ritual = Rituals.objects.create(**ritual_data)
            
            # Get plan type
            plan_type = RitualType.objects.get(id=validated_data['plan_type'])
            
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
                'success': True,
                'message': 'Meditation generated successfully',
                'meditation_id': meditation.id,
                'user_detail': user_detail,
                'ritual': ritual
            }
            
        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error creating meditation: {str(e)}")
            raise MeditationGenerationError('An unexpected error occurred while creating the meditation. Please try again.')

    def generate_meditation(self, plan_type, ritual, user_detail):
        """
        Generate meditation file using local functions based on plan type
        """
        try:
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
                raise PlanTypeNotFoundError(f'Unknown plan type: {plan_type.name}')
            
            # Prepare parameters for the function
            name = ritual.name if ritual and ritual.name else "Meditation"
            goals = user_detail.goals if user_detail and user_detail.goals else ""
            dreamlife = user_detail.dream if user_detail and user_detail.dream else ""
            dream_activities = user_detail.happiness if user_detail and user_detail.happiness else ""
            ritual_type = ritual.ritual_type if ritual and ritual.ritual_type else "Story"
            tone = ritual.tone if ritual and ritual.tone else "Dreamy"
            voice = ritual.voice if ritual and ritual.voice else "female"
            length = int(ritual.duration) if ritual and ritual.duration else 2
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
            if voice not in ["female", "male"]:
                voice = "female"
            
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
                
                return content_file
                
            except Exception as e:
                logger.error(f"Meditation generation failed: {str(e)}")
                return self._create_placeholder_file(plan_type, ritual)
                
        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error in generate_meditation: {str(e)}")
            return self._create_placeholder_file(plan_type, ritual)
    
    def _create_placeholder_file(self, plan_type, ritual):
        """
        Use a default MP3 file from muzic as the placeholder when external API is unavailable
        """
        try:
            # Path to the default MP3 file
            default_mp3_path = os.path.join(os.path.dirname(__file__), 'muzic', 'sleep_manifestation.mp3')
            
            # Generate a unique filename for the placeholder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meditation_{plan_type.name.lower().replace(' ', '_')}_{timestamp}.mp3"

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


class UserLifeVisionSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLifeVision
        fields = [
            'id', 'title', 'description', 'vision_type', 'goal_status', 
            'is_active', 'is_completed', 'priority', 'target_date', 
            'completed_date', 'created_at', 'updated_at', 
            'progress_percentage', 'days_remaining'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_date']
    
    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()
    
    def get_days_remaining(self, obj):
        if obj.target_date:
            from django.utils import timezone
            today = timezone.now().date()
            if obj.target_date > today:
                return (obj.target_date - today).days
            else:
                return 0
        return None
    
    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # If marking as completed, update the completed_date
        if validated_data.get('is_completed') and not instance.is_completed:
            from django.utils import timezone
            validated_data['completed_date'] = timezone.now().date()
            validated_data['goal_status'] = UserLifeVision.GoalStatusChoices.COMPLETED
        
        return super().update(instance, validated_data)


class UserLifeVisionListSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLifeVision
        fields = [
            'id', 'title', 'description', 'vision_type', 'goal_status', 
            'is_active', 'is_completed', 'priority', 'target_date', 
            'progress_percentage', 'created_at'
        ]
    
    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()


class UserLifeVisionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLifeVision
        fields = [
            'title', 'description', 'vision_type', 'goal_status', 
            'priority', 'target_date'
        ]
    
    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserLifeVisionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLifeVision
        fields = [
            'title', 'description', 'vision_type', 'goal_status', 
            'is_active', 'is_completed', 'priority', 'target_date'
        ]

    def update(self, instance, validated_data):
        # If marking as completed, update the completed_date
        if validated_data.get('is_completed', False) and not instance.is_completed:
            instance.completed_date = timezone.now().date()
        
        return super().update(instance, validated_data)


class ExternalMeditationSerializer(serializers.Serializer):
    """
    Serializer for external meditation API requests
    
    The plan_type field accepts a RitualType ID and validates that it exists.
    The validation method returns the ritual type name which is used to determine
    the appropriate external API endpoint.
    
    For choice fields, send the key instead of the value:
    - ritual_type: 'story' (not 'Story')
    - tone: 'dreamy' (not 'Dreamy') 
    - voice: 'female' (not 'Female')
    - duration: '10' (not 10)
    """
    
    # Choice mappings for converting keys to values
    RITUAL_TYPE_CHOICES = {
        'guided_meditations': 'guided_meditations',
        'story': 'story'
    }
    
    TONE_CHOICES = {
        'dreamy': 'dreamy',
        'asmr': 'asmr'
    }
    
    VOICE_CHOICES = {
        'male': 'male',
        'female': 'female'
    }
    
    DURATION_CHOICES = {
        '2': '2',
        '5': '5', 
        '10': '10'
    }
    
    plan_type = serializers.IntegerField(required=True, help_text="Plan type ID to determine API endpoint")
    gender = serializers.CharField(required=True, help_text="User's gender")
    dream = serializers.CharField(required=True, help_text="User's dream")
    goals = serializers.CharField(required=True, help_text="User's goals")
    age_range = serializers.CharField(required=True, help_text="User's age range")
    happiness = serializers.CharField(required=True, help_text="User's happiness level")
    ritual_type = serializers.CharField(required=True, help_text="Ritual type key (e.g., 'story', 'guided_meditations')")
    tone = serializers.CharField(required=True, help_text="Tone key (e.g., 'dreamy', 'asmr')")
    voice = serializers.CharField(required=True, help_text="Voice key (e.g., 'male', 'female')")
    duration = serializers.CharField(required=True, help_text="Duration key (e.g., '2', '5', '10')")
    
    def validate_plan_type(self, value):
        """
        Validate that the plan type ID exists in RitualType model
        """
        try:
            ritual_type = RitualType.objects.get(id=value)
            return value  # Return the ID, not the name
        except RitualType.DoesNotExist:
            raise serializers.ValidationError(
                f"Plan type with ID {value} does not exist."
            )
    
    def validate_ritual_type(self, value):
        """
        Validate ritual_type key and convert to value
        """
        if value not in self.RITUAL_TYPE_CHOICES:
            raise serializers.ValidationError(
                f"Invalid ritual_type key: {value}. Valid keys are: {list(self.RITUAL_TYPE_CHOICES.keys())}"
            )
        return self.RITUAL_TYPE_CHOICES[value]
    
    def validate_tone(self, value):
        """
        Validate tone key and convert to value
        """
        if value not in self.TONE_CHOICES:
            raise serializers.ValidationError(
                f"Invalid tone key: {value}. Valid keys are: {list(self.TONE_CHOICES.keys())}"
            )
        return self.TONE_CHOICES[value]
    
    def validate_voice(self, value):
        """
        Validate voice key and convert to value
        """
        if value not in self.VOICE_CHOICES:
            raise serializers.ValidationError(
                f"Invalid voice key: {value}. Valid keys are: {list(self.VOICE_CHOICES.keys())}"
            )
        return self.VOICE_CHOICES[value]
    
    def validate_duration(self, value):
        """
        Validate duration key and convert to value
        """
        if value not in self.DURATION_CHOICES:
            raise serializers.ValidationError(
                f"Invalid duration key: {value}. Valid keys are: {list(self.DURATION_CHOICES.keys())}"
            )
        return self.DURATION_CHOICES[value]


