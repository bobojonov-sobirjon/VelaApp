from django.core.management.base import BaseCommand
from apps.accounts.notification_service import PushNotificationService
from apps.accounts.models import UserDeviceToken, CustomUser


class Command(BaseCommand):
    help = 'Test push notification system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to test with (optional)',
        )
        parser.add_argument(
            '--device-token',
            type=str,
            help='Device token to test with (optional)',
        )
        parser.add_argument(
            '--device-type',
            type=str,
            choices=['ios', 'android', 'web'],
            help='Device type to test with (optional)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        device_token = options.get('device_token')
        device_type = options.get('device_type')

        # If no user specified, use the first user or create one
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {user_id} does not exist')
                )
                return
        else:
            # Get first user or create one
            user = CustomUser.objects.first()
            if not user:
                user = CustomUser.objects.create(
                    username='testuser',
                    email='test@example.com',
                    first_name='Test',
                    last_name='User'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created test user: {user.username}')
                )

        # If no device token specified, create a test one
        if not device_token:
            device_token = 'test_device_token_12345'

        # If no device type specified, default to android
        if not device_type:
            device_type = 'android'

        # Create or update device token
        device_token_obj, created = UserDeviceToken.objects.get_or_create(
            user=user,
            device_token=device_token,
            defaults={
                'device_type': device_type,
                'app_version': '1.0.0',
                'os_version': '14.0',
                'device_model': 'Test Device',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created device token: {device_token} ({device_type})')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Using existing device token: {device_token} ({device_type})')
            )

        # Test the notification service
        notification_service = PushNotificationService()
        
        self.stdout.write(
            self.style.SUCCESS('Testing push notification service...')
        )

        result = notification_service.send_meditation_library_notification()

        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Notification test successful!\n"
                    f"Message: {result['message']}\n"
                    f"Total devices: {result['total_devices']}\n"
                    f"Successful sends: {result['successful_sends']}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Notification test failed!\n"
                    f"Error: {result['message']}"
                )
            )

        # Show all device tokens for the user
        device_tokens = UserDeviceToken.objects.filter(user=user, is_active=True)
        self.stdout.write(
            self.style.SUCCESS(f'\nActive device tokens for user {user.username}:')
        )
        for token in device_tokens:
            self.stdout.write(
                f"  - {token.device_token} ({token.device_type}) - {token.platform}"
            )
            if token.device_model:
                self.stdout.write(f"    Device: {token.device_model}")
            if token.os_version:
                self.stdout.write(f"    OS: {token.os_version}")
            if token.app_version:
                self.stdout.write(f"    App: {token.app_version}") 