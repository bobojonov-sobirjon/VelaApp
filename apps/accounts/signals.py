from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import MeditationLibrary, PushNotification


@receiver(post_save, sender=MeditationLibrary)
def send_meditation_library_notification(sender, instance, created, **kwargs):
    """
    Send push notification when a new meditation library is created
    """
    if created and not instance.is_deleted:
        # Create push notification record
        notification = PushNotification.objects.create(
            title="New Meditation Library",
            message="A new meditation library has been added to your app.",
            notification_type="meditation_library_added",
            is_sent=False
        )
        
        # Here you would typically call your push notification service
        # For now, we'll just mark it as sent
        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.save() 