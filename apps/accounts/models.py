from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone
from apps.accounts.managers.custom_user import CustomUserManager
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name=_("Email"), null=True, blank=True)
    username = models.CharField(max_length=250, unique=True, verbose_name=_("Username"), null=True, blank=True)
    first_name = models.CharField(max_length=30, verbose_name=_("First Name"), null=True, blank=True)
    last_name = models.CharField(max_length=30, verbose_name=_("Last Name"), null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_("Avatar"))
    is_agree = models.BooleanField(null=True, blank=True, default=False, verbose_name=_("Agreement to Terms"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Staff"))

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True, verbose_name=_("Groups"))

    user_permissions = models.ManyToManyField(Permission, related_name="customuser_set", blank=True,
                                              verbose_name=_("User Permissions"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("1. Users")

    def __str__(self):
        first_name = self.first_name or ""
        last_name = self.last_name or ""
        username = self.username or ""
        email = self.email or ""

        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
        elif username:
            return username
        elif email:
            return email
        else:
            return f"User {self.pk}"


class CustomUserDetail(models.Model):

    class GenderChoices(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='details', verbose_name=_("User"))
    dream = models.TextField(verbose_name=_("Tell me about your dream life"), null=True, blank=True)
    goals = models.TextField(verbose_name=_("Specific goals"), null=True, blank=True)
    age_range = models.CharField(max_length=20, verbose_name=_("Age Range"), null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, verbose_name=_("Gender"), null=True, blank=True)
    happiness = models.TextField(verbose_name=_("What Makes You Happy?"), null=True, blank=True)

    class Meta:
        verbose_name = _("User Detail")
        verbose_name_plural = _("User Details")

    def __str__(self):
        return f"Details for {self.user}"
    
    def get_weekly_login_stats(self):
        """
        Get weekly login statistics for the user (Monday to Sunday)
        Returns a dictionary with login status for each day of the week
        """
        from datetime import datetime, timedelta
        
        # Get current week's Monday and Sunday
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        
        # Get all login records for this week
        week_logins = self.user.login_records.filter(
            login_date__gte=monday,
            login_date__lte=sunday
        ).values_list('login_date', flat=True)
        
        # Create a dictionary for each day of the week
        week_stats = {}
        for i in range(7):
            current_date = monday + timedelta(days=i)
            day_name = current_date.strftime('%A')  # Monday, Tuesday, etc.
            week_stats[day_name] = {
                'date': current_date,
                'logged_in': current_date in week_logins,
                'day_number': i + 1  # 1=Monday, 7=Sunday
            }
        
        return {
            'week_start': monday,
            'week_end': sunday,
            'total_logins_this_week': len(week_logins),
            'days': week_stats
        }


class UserCheckIn(models.Model):
    class CheckInChoices(models.TextChoices):
        STRUGGLING = 'struggling', _('Struggling')
        Neutral = 'neutral', _('Neutral')
        Excellent = 'excellent', _('Excellent')
        
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='check_in', verbose_name=_("User"))
    check_in_choice = models.CharField(max_length=10, choices=CheckInChoices.choices, verbose_name=_("Check In Choice"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    check_in_date = models.DateField(auto_now_add=True, verbose_name=_("Check In Date"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("User Check In")
        verbose_name_plural = _("User Check Ins")
        
    def __str__(self):
        return f"{self.user.username} - {self.check_in_date}"
    
    
class Rituals(models.Model):
    
    class RitualTypeChoices(models.TextChoices):
        Guided = 'guided', _('Guided')
        Story = 'story', _('Story')
    
    class ToneChoices(models.TextChoices):
        DREAMY = 'dreamy', _('Dreamy')
        ASMR = 'asmr', _('ASMR')
    
    class VoiceChoices(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
    
    class DurationChoices(models.TextChoices):
        TWO_MIN = '2', _('2 min')
        FIVE_MIN = '5', _('5 min')
        TEN_MIN = '10', _('10 min')
    
    name = models.CharField(max_length=100, verbose_name=_("Ritual Name"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    
    ritual_type = models.CharField(
        max_length=50, 
        choices=RitualTypeChoices.choices, 
        default=RitualTypeChoices.Guided,
        verbose_name=_("Ritual Type")
    )
    
    tone = models.CharField(
        max_length=50, 
        choices=ToneChoices.choices,
        verbose_name=_("Choose your tone")
    )
    
    voice = models.CharField(
        max_length=50, 
        choices=VoiceChoices.choices, 
        verbose_name=_("Choose your voice")
    )
    
    duration = models.CharField(
        max_length=10, 
        choices=DurationChoices.choices, 
        default=DurationChoices.FIVE_MIN,
        verbose_name=_("Duration")
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Ritual")
        verbose_name_plural = _("Rituals")

    def __str__(self):
        return self.name or f"{self.get_ritual_type_display()} - {self.get_duration_display()}"


class RitualType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Ritual Type Name"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Ritual Type")
        verbose_name_plural = _("2. Ritual Types")
    
    def __str__(self):
        return self.name
    
class MeditationGenerate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='meditations', verbose_name=_("User"))
    details = models.ForeignKey(Rituals, on_delete=models.CASCADE, related_name='custom_ritual', verbose_name=_("Customize Ritual"))
    ritual_type = models.ForeignKey(RitualType, on_delete=models.CASCADE, related_name='custom_ritual_type', verbose_name=_("Ritual Type"))
    file = models.FileField(upload_to='meditations/', blank=True, null=True, verbose_name=_("File"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Meditation")
        verbose_name_plural = _("3. Meditations")
        
    def __str__(self):
        return f"{self.user.username} - {self.details.name}"


class LikeMeditation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='like_meditation', verbose_name=_("User"))
    meditation = models.ForeignKey(MeditationGenerate, on_delete=models.CASCADE, related_name='like_meditation', verbose_name=_("Meditation"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Like Meditation")
        verbose_name_plural = _("Like Meditations")
        
    def __str__(self):
        return f"{self.user.username} - {self.meditation.details.name}"
    

class MeditationLibrary(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    image = models.ImageField(upload_to='meditation_library/', blank=True, null=True, verbose_name=_("Image"))
    file = models.FileField(upload_to='meditation_library/', blank=True, null=True, verbose_name=_("File"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Meditation Library")
        verbose_name_plural = _("4. Meditation Libraries")
        
    def __str__(self):
        return self.name

class UserLoginTracker(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_records', verbose_name=_("User"))
    login_date = models.DateField(auto_now_add=True, verbose_name=_("Login Date"))
    login_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Login Time"))
    
    class Meta:
        verbose_name = _("User Login Tracker")
        verbose_name_plural = _("6. User Login Trackers")
        unique_together = ['user', 'login_date']  # Only one record per day per user
    
    def __str__(self):
        return f"{self.user} - {self.login_date}"
    
    @classmethod
    def record_login(cls, user):
        """Record user login for today if not already recorded"""
        today = timezone.now().date()
        login_record, created = cls.objects.get_or_create(
            user=user,
            login_date=today,
            defaults={'login_time': timezone.now()}
        )
        return login_record


class Plans(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Plan Name"), null=True, blank=True)
    price = models.FloatField(default=0.00, verbose_name=_("Price"), null=True, blank=True)
    is_monthly = models.BooleanField(default=True, verbose_name=_("Monthly Plan"), null=True, blank=True)
    is_annual = models.BooleanField(default=False, verbose_name=_("Annual Plan"), null=True, blank=True)
    is_free_trial = models.BooleanField(default=False, verbose_name=_("Free Trial"), null=True, blank=True)
    discount = models.FloatField(default=0.00, verbose_name=_("Discount"), null=True, blank=True)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("5. Plans")

    def __str__(self):
        return self.name
    

class UserPlan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_plans', verbose_name=_("User"))
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='user_plans', verbose_name=_("Plan"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Start Date"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("End Date"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("User Plan")
        verbose_name_plural = _("User Plans")
        unique_together = ['user', 'plan']
    
    def __str__(self):
        return f"{self.user} - {self.plan.name}"


class PlanDescriptin(models.Model):
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='plan_description', verbose_name=_("Plan"))
    title = models.CharField(max_length=100, verbose_name=_("Title"), null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Plan Description")
        verbose_name_plural = _("Plan Descriptions")


class UserLifeVision(models.Model):
    class VisionTypeChoices(models.TextChoices):
        LIFE_VISION = 'life_vision', _('Life Vision')
        GOAL = 'goal', _('Goal')
        DREAM = 'dream', _('Dream')
        NORTH_STAR = 'north_star', _('North Star')
    
    class GoalStatusChoices(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        NOT_STARTED = 'not_started', _('Not Started')
        PAUSED = 'paused', _('Paused')
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='life_visions', verbose_name=_("User"))
    title = models.CharField(max_length=200, verbose_name=_("Title"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    vision_type = models.CharField(
        max_length=20, 
        choices=VisionTypeChoices.choices, 
        default=VisionTypeChoices.LIFE_VISION,
        verbose_name=_("Vision Type")
    )
    goal_status = models.CharField(
        max_length=20, 
        choices=GoalStatusChoices.choices, 
        default=GoalStatusChoices.NOT_STARTED,
        verbose_name=_("Goal Status")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    priority = models.IntegerField(default=1, verbose_name=_("Priority"))
    target_date = models.DateField(null=True, blank=True, verbose_name=_("Target Date"))
    completed_date = models.DateField(null=True, blank=True, verbose_name=_("Completed Date"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("User Life Vision")
        verbose_name_plural = _("7. User Life Visions")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_completed(self):
        """Mark the goal as completed"""
        from django.utils import timezone
        self.is_completed = True
        self.goal_status = self.GoalStatusChoices.COMPLETED
        self.completed_date = timezone.now().date()
        self.save()
    
    def get_progress_percentage(self):
        """Calculate progress percentage based on goal status"""
        if self.is_completed:
            return 100
        elif self.goal_status == self.GoalStatusChoices.IN_PROGRESS:
            return 50
        elif self.goal_status == self.GoalStatusChoices.PAUSED:
            return 25
        else:
            return 0


