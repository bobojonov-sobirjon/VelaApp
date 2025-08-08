from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from apps.accounts.models import (
    CustomUser, 
    Rituals,
    RitualType,
    MeditationGenerate,
    Plans,
    MeditationLibrary,
    PlanDescriptin,
    CustomUserDetail,
    LikeMeditation,
    UserCheckIn,
    UserLifeVision,
    PushNotification,
    UserDeviceToken,
)
from apps.accounts.notification_service import PushNotificationService


class CustomUserDetailInline(admin.TabularInline):
    model = CustomUserDetail
    extra = 0
    fields = ('dream', 'goals', 'age_range', 'gender', 'happiness', 'occupation', 'interests', 'meditation_experience', 'stress_level', 'sleep_quality', 'preferred_meditation_time')
    verbose_name = _("User Detail")
    verbose_name_plural = _("User Details")


class UserCheckInInline(admin.TabularInline):
    model = UserCheckIn
    extra = 0
    fields = ('check_in_choice', 'description')
    readonly_fields = ('check_in_date',)
    verbose_name = _("User Check In")
    verbose_name_plural = _("User Check Ins")


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    inlines = [CustomUserDetailInline, UserCheckInInline]

    fieldsets = (
        (None, {'fields': ('username', 'password', 'avatar')}),
        (_('Personal Information'),
         {'fields': ('first_name', 'last_name', 'email', 'is_agree')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Groups and Permissions'), {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'avatar',
                'is_agree', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
        }),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('id',)
    filter_horizontal = ('groups', 'user_permissions')


class RitualTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')


class LikeMeditationInline(admin.TabularInline):
    model = LikeMeditation
    extra = 0
    fields = ('meditation',)
    verbose_name = _("Like Meditation")
    verbose_name_plural = _("Like Meditations")
    

class MeditationGenerateAdmin(admin.ModelAdmin):
    list_display = ('user', 'details_name', 'ritual_type_name', 'details_tone', 'details_voice', 'details_duration', 'file', 'created_at', 'is_deleted')
    list_filter = ('ritual_type', 'created_at', 'details__ritual_type', 'details__tone', 'details__voice', 'details__duration', 'is_deleted')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'details__name', 'details__description', 'ritual_type__name', 'ritual_type__description')
    ordering = ('-created_at',)
    list_select_related = ('user', 'details', 'ritual_type')
    
    fieldsets = (
        (_('User Information'), {'fields': ('user',)}),
        (_('Ritual Information'), {
            'fields': ('details_name_display', 'details_description_display', 'details_tone_display', 'details_voice_display', 'details_duration_display'),
        }),
        (_('Ritual Type Information'), {
            'fields': ('ritual_type_name_display', 'ritual_type_description_display'),
        }),
        (_('File'), {'fields': ('file',)}),
        (_('Status'), {'fields': ('is_deleted',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at', 'details_name_display', 'details_description_display', 'details_tone_display', 'details_voice_display', 'details_duration_display', 'ritual_type_name_display', 'ritual_type_description_display')
    inlines = [LikeMeditationInline]
    
    def details_name(self, obj):
        if obj.details:
            return obj.details.name or "No name"
        return "-"
    details_name.short_description = _("Ritual Name")
    
    def details_tone(self, obj):
        if obj.details:
            return obj.details.get_tone_display()
        return "-"
    details_tone.short_description = _("Tone")
    
    def details_voice(self, obj):
        if obj.details:
            return obj.details.get_voice_display()
        return "-"
    details_voice.short_description = _("Voice")
    
    def details_duration(self, obj):
        if obj.details:
            return obj.details.get_duration_display()
        return "-"
    details_duration.short_description = _("Duration")
    
    def ritual_type_name(self, obj):
        if obj.ritual_type:
            return obj.ritual_type.name or "No name"
        return "-"
    ritual_type_name.short_description = _("Ritual Type")
    
    # Display methods for readonly fields
    def details_name_display(self, obj):
        if obj.details:
            return obj.details.name or "No name"
        return "-"
    details_name_display.short_description = _("Ritual Name")
    
    def details_description_display(self, obj):
        if obj.details and obj.details.description:
            return obj.details.description
        return "-"
    details_description_display.short_description = _("Ritual Description")
    
    def details_tone_display(self, obj):
        if obj.details:
            return obj.details.get_tone_display()
        return "-"
    details_tone_display.short_description = _("Tone")
    
    def details_voice_display(self, obj):
        if obj.details:
            return obj.details.get_voice_display()
        return "-"
    details_voice_display.short_description = _("Voice")
    
    def details_duration_display(self, obj):
        if obj.details:
            return obj.details.get_duration_display()
        return "-"
    details_duration_display.short_description = _("Duration")
    
    def ritual_type_name_display(self, obj):
        if obj.ritual_type:
            return obj.ritual_type.name or "No name"
        return "-"
    ritual_type_name_display.short_description = _("Ritual Type Name")
    
    def ritual_type_description_display(self, obj):
        if obj.ritual_type and obj.ritual_type.description:
            return obj.ritual_type.description
        return "-"
    ritual_type_description_display.short_description = _("Ritual Type Description")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'details', 'ritual_type')


class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'is_sent', 'sent_at', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'created_at')
    search_fields = ('title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('title', 'message', 'notification_type')}),
        (_('Status'), {'fields': ('is_sent', 'sent_at')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class UserDeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'platform', 'device_model', 'app_version', 'os_version', 'is_active', 'created_at')
    list_filter = ('device_type', 'platform', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'device_token', 'device_model')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('user', 'device_token', 'device_type', 'platform')}),
        (_('Device Information'), {'fields': ('device_model', 'os_version', 'app_version')}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class MeditationLibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview', 'description_preview', 'file_preview', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'is_deleted')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        (_('Media'), {'fields': ('image', 'image_preview', 'file', 'file_preview')}),
        (_('Status'), {'fields': ('is_deleted',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at', 'image_preview', 'file_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px; object-fit: cover; border-radius: 4px;" />')
        return mark_safe('<span style="color: #999;">No image</span>')
    image_preview.short_description = _("Image Preview")
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"
    description_preview.short_description = _("Description")
    
    def file_preview(self, obj):
        if obj.file:
            filename = obj.file.name.split('/')[-1]
            return mark_safe(f'<a href="{obj.file.url}" target="_blank">{filename}</a>')
        return mark_safe('<span style="color: #999;">No file</span>')
    file_preview.short_description = _("File")
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """Override save to send notification when new meditation library is created"""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # Send notification only for new meditation libraries that are not deleted
        if is_new and not obj.is_deleted:
            notification_service = PushNotificationService()
            result = notification_service.send_meditation_library_notification()
            
            # You can add a message to the admin interface here if needed
            if result['success']:
                self.message_user(request, f"Meditation library created and notification sent to {result.get('successful_sends', 0)} devices.")
            else:
                self.message_user(request, f"Meditation library created but notification failed: {result.get('message', 'Unknown error')}")


class PlanDescriptionInline(admin.TabularInline):
    model = PlanDescriptin
    extra = 0
    fields = ('title', 'description')
    verbose_name = _("Plan Description")
    verbose_name_plural = _("Plan Steps")


class PlansAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_monthly', 'is_annual', 'is_free_trial', 'discount')
    list_filter = ('is_monthly', 'is_annual', 'is_free_trial')
    search_fields = ('name',)
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'price')}),
        (_('Plan Type'), {'fields': ('is_monthly', 'is_annual', 'is_free_trial', 'discount')}),
    )
    inlines = [PlanDescriptionInline]
    
class UserLifeVisionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'vision_type', 'goal_status', 'is_active', 'is_completed', 'priority', 'target_date', 'completed_date', 'created_at', 'updated_at')
    list_filter = ('vision_type', 'goal_status', 'is_active', 'is_completed', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    ordering = ('title',)
    


# Register all models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RitualType, RitualTypeAdmin)
admin.site.register(MeditationGenerate, MeditationGenerateAdmin)
admin.site.register(MeditationLibrary, MeditationLibraryAdmin)
admin.site.register(Plans, PlansAdmin)
admin.site.register(UserLifeVision, UserLifeVisionAdmin)
admin.site.register(PushNotification, PushNotificationAdmin)
admin.site.register(UserDeviceToken, UserDeviceTokenAdmin)

# Customize admin site
admin.site.site_header = _("Vela Admin")
admin.site.site_title = _("Vela Admin")
admin.site.index_title = _("Welcome to Vela Admin")

# Unregister Sites model as it's not needed
admin.site.unregister(Site)
admin.site.unregister(Group)