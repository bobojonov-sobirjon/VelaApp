import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import PushNotification, UserDeviceToken

# Firebase Admin SDK uchun
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    from firebase_admin.exceptions import FirebaseError
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class PushNotificationService:
    """Service for sending push notifications to mobile apps"""
    
    def __init__(self):
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.fcm_url = 'https://fcm.googleapis.com/fcm/send'
        
        # Firebase Admin SDK ni ishga tushirish
        if FIREBASE_AVAILABLE and not firebase_admin._apps:
            try:
                # Service account JSON faylini yuklash
                cred = credentials.Certificate('c:/Users/asus/Downloads/vela-5d961-firebase-adminsdk-fbsvc-4c2e0f953e.json')
                firebase_admin.initialize_app(cred)
                self.use_firebase_admin = True
            except Exception as e:
                print(f"Firebase Admin SDK error: {e}")
                self.use_firebase_admin = False
        else:
            self.use_firebase_admin = FIREBASE_AVAILABLE
    
    def send_notification_to_all_users(self, title, message, notification_type="general"):
        """
        Send push notification to all active users
        """
        try:
            # Get all active device tokens
            device_tokens = UserDeviceToken.objects.filter(is_active=True).values_list('device_token', flat=True)
            
            if not device_tokens:
                return {
                    'success': False,
                    'message': 'No active device tokens found',
                    'total_devices': 0,
                    'successful_sends': 0
                }
            
            successful_sends = 0
            
            if self.use_firebase_admin:
                # Firebase Admin SDK orqali yuborish
                successful_sends = self._send_with_firebase_admin(device_tokens, title, message)
            else:
                # Legacy FCM Server Key orqali yuborish
                successful_sends = self._send_with_legacy_fcm(device_tokens, title, message)
            
            # Create notification record
            notification = PushNotification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                is_sent=True,
                sent_at=timezone.now()
            )
            
            return {
                'success': True,
                'message': f'Notification sent to {successful_sends} devices',
                'total_devices': len(device_tokens),
                'successful_sends': successful_sends
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error sending notifications: {str(e)}',
                'total_devices': 0,
                'successful_sends': 0
            }
    
    def _send_with_firebase_admin(self, device_tokens, title, message):
        """Firebase Admin SDK orqali yuborish"""
        try:
            print(f"Firebase Admin SDK: Sending to {len(device_tokens)} devices")
            successful_sends = 0
            
            for token in device_tokens:
                try:
                    print(f"Trying to send to token: {token[:30]}...")
                    
                    # Create message for each token
                    message_obj = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=message
                        ),
                        data={
                            'title': title,
                            'message': message,
                            'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                        },
                        token=token
                    )
                    
                    # Send message
                    response = messaging.send(message_obj)
                    successful_sends += 1
                    print(f"✅ Successfully sent to token: {token[:20]}...")
                    
                except Exception as e:
                    print(f"❌ Failed to send to token {token[:20]}...: {e}")
            
            print(f"Firebase Admin SDK: {successful_sends}/{len(device_tokens)} messages sent successfully")
            return successful_sends
            
        except FirebaseError as e:
            print(f"Firebase Admin SDK error: {e}")
            return 0
        except Exception as e:
            print(f"Error with Firebase Admin SDK: {e}")
            return 0
    
    def _send_with_legacy_fcm(self, device_tokens, title, message):
        """Legacy FCM Server Key orqali yuborish"""
        if not self.fcm_server_key:
            print("FCM Server Key not configured")
            return 0
        
        try:
            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }
            
            successful_sends = 0
            
            for token in device_tokens:
                payload = {
                    'to': token,
                    'notification': {
                        'title': title,
                        'body': message,
                        'sound': 'default'
                    },
                    'data': {
                        'title': title,
                        'message': message,
                        'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                    }
                }
                
                response = requests.post(self.fcm_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') == 1:
                        successful_sends += 1
                
            return successful_sends
            
        except Exception as e:
            print(f"Legacy FCM error: {e}")
            return 0
    
    def send_meditation_library_notification(self):
        """
        Send notification when new meditation library is added
        """
        return self.send_notification_to_all_users(
            title="New Meditation Library",
            message="A new meditation library has been added to your app.",
            notification_type="meditation_library_added"
        ) 