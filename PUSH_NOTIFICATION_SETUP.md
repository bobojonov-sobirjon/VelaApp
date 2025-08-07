# Push Notification System Setup

This document explains how to set up and use the push notification system for the Vela meditation app.

## Overview

The push notification system automatically sends notifications to all users when a new meditation library is added through the admin panel. The notification message is: "A new meditation library has been added to your app."

**NEW FEATURE**: The system now automatically detects the user's platform (iOS/Android/Web) from the request headers, so mobile apps don't need to specify the device type!

## Components

### 1. Models

- **PushNotification**: Stores notification records
- **UserDeviceToken**: Stores device tokens for mobile apps with auto-detected platform

### 2. Services

- **PushNotificationService**: Handles sending notifications via Firebase Cloud Messaging (FCM)

### 3. Signals

- **send_meditation_library_notification**: Automatically triggers when MeditationLibrary is created

### 4. API Endpoints

- **POST /api/device-token/**: Register device token for push notifications (auto-detects platform)
- **DELETE /api/device-token/**: Unregister device token

## Setup Instructions

### 1. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing project
3. Go to Project Settings > Service Accounts
4. Generate a new private key
5. Copy the server key from the generated JSON file

### 2. Django Settings

Add your Firebase server key to `config/settings.py`:

```python
# Push Notification Settings
FCM_SERVER_KEY = 'your_actual_fcm_server_key_here'
```

### 3. Database Migration

Run migrations to create the notification tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Usage

### 1. Admin Panel

When you add a new meditation library through the Django admin panel:
1. Go to `/admin/`
2. Navigate to "4. Meditation Libraries"
3. Click "Add Meditation Library"
4. Fill in the details and save
5. The system will automatically send notifications to all registered devices

### 2. Mobile App Integration

#### Register Device Token (Simplified!)

**NEW**: You only need to send the device token! The platform is auto-detected.

```bash
POST /api/device-token/
Content-Type: application/json
Authorization: Bearer <your_jwt_token>

{
    "device_token": "your_fcm_device_token"
}
```

**Optional fields** (if you want to provide additional info):
```bash
{
    "device_token": "your_fcm_device_token",
    "device_type": "ios",  // optional - auto-detected if not provided
    "app_version": "1.0.0",  // optional
    "os_version": "14.0",  // optional
    "device_model": "iPhone 12"  // optional
}
```

**Response**:
```json
{
    "message": "Device token registered successfully",
    "device_token_id": 1,
    "detected_platform": "ios"
}
```

#### Unregister Device Token

```bash
DELETE /api/device-token/
Content-Type: application/json
Authorization: Bearer <your_jwt_token>

{
    "device_token": "your_fcm_device_token"
}
```

### 3. Testing

Test the notification system:

```bash
python manage.py test_notification
```

Or test with specific user and device token:

```bash
python manage.py test_notification --user-id 1 --device-token "your_test_token" --device-type ios
```

## Mobile App Implementation

### Flutter Example (Simplified!)

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

class NotificationService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

  Future<void> initialize() async {
    // Request permission
    NotificationSettings settings = await _firebaseMessaging.requestPermission();
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      // Get device token
      String? token = await _firebaseMessaging.getToken();
      
      if (token != null) {
        // Register token with your backend (platform auto-detected!)
        await registerDeviceToken(token);
      }
    }
  }

  Future<void> registerDeviceToken(String token) async {
    final response = await http.post(
      Uri.parse('your_api_url/api/device-token/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $userToken',
      },
      body: jsonEncode({
        'device_token': token,
        // No need to specify device_type - it's auto-detected!
        'app_version': '1.0.0',  // optional
        'os_version': '14.0',    // optional
        'device_model': 'iPhone 12'  // optional
      }),
    );
    
    final responseData = jsonDecode(response.body);
    print('Platform detected: ${responseData['detected_platform']}');
  }
}
```

### React Native Example (Simplified!)

```javascript
import messaging from '@react-native-firebase/messaging';

class NotificationService {
  async initialize() {
    // Request permission
    const authStatus = await messaging().requestPermission();
    
    if (authStatus === messaging.AuthorizationStatus.AUTHORIZED) {
      // Get device token
      const token = await messaging().getToken();
      
      if (token) {
        // Register token with your backend (platform auto-detected!)
        await this.registerDeviceToken(token);
      }
    }
  }

  async registerDeviceToken(token) {
    const response = await fetch('your_api_url/api/device-token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}`,
      },
      body: JSON.stringify({
        device_token: token,
        // No need to specify device_type - it's auto-detected!
        app_version: '1.0.0',  // optional
        os_version: '14.0',    // optional
        device_model: 'iPhone 12'  // optional
      }),
    });
    
    const responseData = await response.json();
    console.log('Platform detected:', responseData.detected_platform);
  }
}
```

## Auto-Detection Features

### Platform Detection

The system automatically detects the platform from the request headers:

- **iOS**: Detects iPhone, iPad, iPod in User-Agent
- **Android**: Detects "android" in User-Agent  
- **Web**: Detects Mozilla, Chrome, Safari in User-Agent
- **Default**: Falls back to "web" if can't detect

### Device Information

The system now stores additional device information:

- **Platform**: Auto-detected platform (iOS/Android/Web)
- **App Version**: Optional app version
- **OS Version**: Optional operating system version
- **Device Model**: Optional device model

## Admin Panel Features

### Push Notifications Management

- View all sent notifications
- Check notification status (sent/not sent)
- Monitor notification history

### User Device Tokens Management

- View all registered device tokens with auto-detected platform
- Monitor active/inactive tokens
- See device information (model, OS version, app version)
- Filter by device type and platform

## Troubleshooting

### Common Issues

1. **No notifications sent**: Check if FCM_SERVER_KEY is set correctly
2. **Device not receiving notifications**: Verify device token is registered and active
3. **Admin panel errors**: Check if migrations are applied correctly
4. **Platform not detected**: Check User-Agent header in request

### Debug Commands

```bash
# Check notification records
python manage.py shell
>>> from apps.accounts.models import PushNotification
>>> PushNotification.objects.all()

# Check device tokens with platform info
>>> from apps.accounts.models import UserDeviceToken
>>> UserDeviceToken.objects.filter(is_active=True).values('device_token', 'device_type', 'platform', 'device_model')
```

## Security Considerations

1. **FCM Server Key**: Keep your FCM server key secure and never commit it to version control
2. **Device Tokens**: Validate device tokens on the server side
3. **Rate Limiting**: Consider implementing rate limiting for device token registration
4. **Token Expiration**: Implement token refresh mechanisms for long-lived tokens
5. **Platform Validation**: The system validates detected platforms against allowed values

## Future Enhancements

1. **Notification Templates**: Support for different notification types
2. **Targeted Notifications**: Send notifications to specific user groups
3. **Notification History**: Track notification delivery and engagement
4. **Scheduled Notifications**: Send notifications at specific times
5. **Rich Notifications**: Support for images and action buttons
6. **Advanced Platform Detection**: More sophisticated platform detection algorithms 