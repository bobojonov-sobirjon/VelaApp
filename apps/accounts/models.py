from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    email = models.EmailField(_('Email'), unique=True, blank=True, null=True)
    username = models.CharField(_('Username'), max_length=250, unique=True, blank=True, null=True)
    first_name = models.CharField(_('First Name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('Last Name'), max_length=30, blank=True, null=True)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True, null=True)
    is_agree = models.BooleanField(_('Agreement to Terms'), default=False, blank=True, null=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('1. Users')

    def __str__(self):
        return self.username or self.email or str(self.id)


class RitualType(models.Model):
    """
    Model for different types of rituals
    """
    name = models.CharField(_('Ritual Type Name'), max_length=100, blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Ritual Type')
        verbose_name_plural = _('2. Ritual Types')

    def __str__(self):
        return self.name or str(self.id)


class Rituals(models.Model):
    """
    Model for ritual configurations
    """
    RITUAL_TYPE_CHOICES = [
        ('guided', 'Guided'),
        ('story', 'Story'),
    ]
    TONE_CHOICES = [
        ('dreamy', 'Dreamy'),
        ('asmr', 'ASMR'),
    ]
    VOICE_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    DURATION_CHOICES = [
        ('2', '2 min'),
        ('5', '5 min'),
        ('10', '10 min'),
    ]

    name = models.CharField(_('Ritual Name'), max_length=100, blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    ritual_type = models.CharField(
        _('Ritual Type'),
        max_length=50,
        choices=RITUAL_TYPE_CHOICES,
        default='guided'
    )
    tone = models.CharField(_('Choose your tone'), max_length=50, choices=TONE_CHOICES)
    voice = models.CharField(_('Choose your voice'), max_length=50, choices=VOICE_CHOICES)
    duration = models.CharField(
        _('Duration'),
        max_length=10,
        choices=DURATION_CHOICES,
        default='5'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Ritual')
        verbose_name_plural = _('Rituals')

    def __str__(self):
        return self.name or str(self.id)


class MeditationLibrary(models.Model):
    """
    Model for meditation library items
    """
    name = models.CharField(_('Name'), max_length=100, blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    image = models.ImageField(_('Image'), upload_to='meditation_library/', blank=True, null=True)
    file = models.FileField(_('File'), upload_to='meditation_library/', blank=True, null=True)
    is_deleted = models.BooleanField(_('Is Deleted'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Meditation Library')
        verbose_name_plural = _('4. Meditation Libraries')

    def __str__(self):
        return self.name or str(self.id)


class Plans(models.Model):
    """
    Model for subscription plans
    """
    name = models.CharField(_('Plan Name'), max_length=100, blank=True, null=True)
    price = models.FloatField(_('Price'), default=0.0, blank=True, null=True)
    is_monthly = models.BooleanField(_('Monthly Plan'), default=True, blank=True, null=True)
    is_annual = models.BooleanField(_('Annual Plan'), default=False, blank=True, null=True)
    is_free_trial = models.BooleanField(_('Free Trial'), default=False, blank=True, null=True)
    discount = models.FloatField(_('Discount'), default=0.0, blank=True, null=True)

    class Meta:
        verbose_name = _('Plan')
        verbose_name_plural = _('5. Plans')

    def __str__(self):
        return self.name or str(self.id)


class PlanDescriptin(models.Model):
    """
    Model for plan descriptions/steps
    """
    title = models.CharField(_('Title'), max_length=100, blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='plan_description', verbose_name=_('Plan'))

    class Meta:
        verbose_name = _('Plan Description')
        verbose_name_plural = _('Plan Descriptions')

    def __str__(self):
        return self.title or str(self.id)


class CustomUserDetail(models.Model):
    """
    Model for additional user details
    """
    class GenderChoices(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
    
    class AgeRangeChoices(models.TextChoices):
        AGE_18_24 = '18-24', _('18-24')
        AGE_25_34 = '25-34', _('25-34')
        AGE_35_44 = '35-44', _('35-44')
        AGE_45_54 = '45-54', _('45-54')
        AGE_55_64 = '55-64', _('55-64')
        AGE_65_PLUS = '65+', _('65+')

    dream = models.TextField(_('Tell me about your dream life'), blank=True, null=True)
    goals = models.TextField(_('Specific goals'), blank=True, null=True)
    age_range = models.CharField(_('Age Range'), max_length=20, blank=True, null=True)
    gender = models.CharField(_('Gender'), max_length=10, choices=GenderChoices.choices, blank=True, null=True)
    happiness = models.TextField(_('What Makes You Happy?'), blank=True, null=True)
    occupation = models.CharField(_('Occupation'), max_length=100, blank=True, null=True)
    interests = models.TextField(_('Interests'), blank=True, null=True)
    meditation_experience = models.CharField(_('Meditation Experience'), max_length=50, blank=True, null=True)
    stress_level = models.CharField(_('Stress Level'), max_length=50, blank=True, null=True)
    sleep_quality = models.CharField(_('Sleep Quality'), max_length=50, blank=True, null=True)
    preferred_meditation_time = models.CharField(_('Preferred Meditation Time'), max_length=50, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='details', verbose_name=_('User'))

    class Meta:
        verbose_name = _('User Detail')
        verbose_name_plural = _('User Details')

    def __str__(self):
        return f"Details for {self.user.username or self.user.email}"


class MeditationGenerate(models.Model):
    """
    Model for generated meditations
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='meditations', verbose_name=_('User'))
    details = models.ForeignKey(Rituals, on_delete=models.CASCADE, related_name='custom_ritual', verbose_name=_('Customize Ritual'))
    ritual_type = models.ForeignKey(RitualType, on_delete=models.CASCADE, related_name='custom_ritual_type', verbose_name=_('Ritual Type'))
    file = models.FileField(_('File'), upload_to='meditations/', blank=True, null=True)
    is_deleted = models.BooleanField(_('Is Deleted'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Meditation')
        verbose_name_plural = _('3. Meditations')

    def __str__(self):
        return f"Meditation for {self.user.username or self.user.email}"


class LikeMeditation(models.Model):
    """
    Model for user meditation likes
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='like_meditation', verbose_name=_('User'))
    meditation = models.ForeignKey(MeditationGenerate, on_delete=models.CASCADE, related_name='like_meditation', verbose_name=_('Meditation'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Like Meditation')
        verbose_name_plural = _('Like Meditations')

    def __str__(self):
        return f"{self.user.username or self.user.email} likes {self.meditation}"


class UserCheckIn(models.Model):
    """
    Model for user check-ins
    """
    class CheckInChoices(models.TextChoices):
        STRUGGLING = 'struggling', _('Struggling')
        NEUTRAL = 'neutral', _('Neutral')
        EXCELLENT = 'excellent', _('Excellent')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='check_in', verbose_name=_('User'))
    check_in_choice = models.CharField(_('Check In Choice'), max_length=10, choices=CheckInChoices.choices, blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    check_in_date = models.DateField(_('Check In Date'), auto_now_add=True)

    class Meta:
        verbose_name = _('User Check In')
        verbose_name_plural = _('User Check Ins')

    def __str__(self):
        return f"Check-in for {self.user.username or self.user.email} on {self.check_in_date}"


class UserLifeVision(models.Model):
    """
    Model for user life vision/goals
    """
    class VisionTypeChoices(models.TextChoices):
        PERSONAL = 'personal', _('Personal')
        PROFESSIONAL = 'professional', _('Professional')
        HEALTH = 'health', _('Health')
        RELATIONSHIP = 'relationship', _('Relationship')
        FINANCIAL = 'financial', _('Financial')
        SPIRITUAL = 'spiritual', _('Spiritual')

    class GoalStatusChoices(models.TextChoices):
        NOT_STARTED = 'not_started', _('Not Started')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        ON_HOLD = 'on_hold', _('On Hold')

    class PriorityChoices(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='life_visions', verbose_name=_('User'))
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True, null=True)
    vision_type = models.CharField(_('Vision Type'), max_length=20, choices=VisionTypeChoices.choices)
    goal_status = models.CharField(_('Goal Status'), max_length=20, choices=GoalStatusChoices.choices, default='not_started')
    is_active = models.BooleanField(_('Active'), default=True)
    is_completed = models.BooleanField(_('Completed'), default=False)
    priority = models.CharField(_('Priority'), max_length=10, choices=PriorityChoices.choices, default='medium')
    target_date = models.DateField(_('Target Date'), blank=True, null=True)
    completed_date = models.DateField(_('Completed Date'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('User Life Vision')
        verbose_name_plural = _('User Life Visions')

    def __str__(self):
        return f"{self.title} - {self.user.username or self.user.email}"


class PushNotification(models.Model):
    """
    Model for push notifications
    """
    title = models.CharField(_('Title'), max_length=200)
    message = models.TextField(_('Message'))
    notification_type = models.CharField(_('Notification Type'), max_length=50)
    is_sent = models.BooleanField(_('Is Sent'), default=False)
    sent_at = models.DateTimeField(_('Sent At'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Push Notification')
        verbose_name_plural = _('8. Push Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserDeviceToken(models.Model):
    """
    Model for user device tokens
    """
    class DeviceTypeChoices(models.TextChoices):
        MOBILE = 'mobile', _('Mobile')
        TABLET = 'tablet', _('Tablet')
        DESKTOP = 'desktop', _('Desktop')

    class PlatformChoices(models.TextChoices):
        IOS = 'ios', _('iOS')
        ANDROID = 'android', _('Android')
        WEB = 'web', _('Web')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='device_tokens', verbose_name=_('User'))
    device_token = models.CharField(_('Device Token'), max_length=500)
    device_type = models.CharField(_('Device Type'), max_length=20, choices=DeviceTypeChoices.choices)
    platform = models.CharField(_('Platform'), max_length=20, choices=PlatformChoices.choices)
    device_model = models.CharField(_('Device Model'), max_length=100, blank=True, null=True)
    app_version = models.CharField(_('App Version'), max_length=20, blank=True, null=True)
    os_version = models.CharField(_('OS Version'), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('User Device Token')
        verbose_name_plural = _('User Device Tokens')

    def __str__(self):
        return f"{self.user.username or self.user.email} - {self.device_type}"


class UserPlan(models.Model):
    """
    Model for user subscription plans
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_plans', verbose_name=_('User'))
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='user_plans', verbose_name=_('Plan'))
    is_active = models.BooleanField(_('Active'), default=True)
    start_date = models.DateTimeField(_('Start Date'), auto_now_add=True)
    end_date = models.DateTimeField(_('End Date'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('User Plan')
        verbose_name_plural = _('User Plans')

    def __str__(self):
        return f"{self.user.username or self.user.email} - {self.plan.name}" 