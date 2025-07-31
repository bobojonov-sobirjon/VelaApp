# Environment Variables Setup

You need to create a `.env` file in your project root directory with the following variables:

## Create .env file

Create a file named `.env` in your project root (same level as `manage.py`) with the following content:

```bash
# Django Settings
SECRET_KEY=django-insecure-04e5xdoalt@b9z25p(uqa&!j!14j65yih9n!b_4q7lelybcy4z
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth Settings
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=https://your-domain.com/api/accounts/google/callback/

# Facebook OAuth Settings
FACEBOOK_APP_ID=your_facebook_app_id_here
FACEBOOK_APP_SECRET=your_facebook_app_secret_here
FACEBOOK_REDIRECT_URI=https://your-domain.com/api/accounts/facebook/callback/

# Apple ID OAuth Settings
APPLE_CLIENT_ID=your_apple_client_id_here
APPLE_TEAM_ID=your_apple_team_id_here
APPLE_KEY_ID=your_apple_key_id_here
APPLE_PRIVATE_KEY=your_apple_private_key_here

# External API Configuration
MEDITATION_API_BASE_URL=http://31.97.98.47:8000
MEDITATION_API_TIMEOUT=10
MEDITATION_API_ENABLED=True
```

## How to get the values:

### Google OAuth:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set application type to "Web application"
6. Add your redirect URI
7. Copy the Client ID and Client Secret

### Facebook OAuth:
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Go to Settings → Basic
5. Copy the App ID and App Secret
6. Add your redirect URI in Facebook Login settings

### Apple ID:
1. Go to [Apple Developer](https://developer.apple.com/)
2. Create a new App ID
3. Enable Sign In with Apple
4. Create a Services ID
5. Generate a private key
6. Copy the Team ID, Key ID, and Client ID

## Testing the setup:

After creating the `.env` file, restart your Django server and test:

```python
# In Django shell or view
from django.conf import settings
print(settings.GOOGLE_CLIENT_ID)
print(settings.FACEBOOK_APP_ID)
print(settings.APPLE_CLIENT_ID)
```

If you see the values (not empty strings), the setup is working correctly.

## Important Notes:

1. **Never commit your `.env` file** to version control
2. **Use different values for development and production**
3. **Keep your secrets secure**
4. **Use HTTPS in production**

## Troubleshooting:

If you still see empty values:

1. Make sure the `.env` file is in the project root
2. Check that `python-dotenv` is installed: `pip install python-dotenv`
3. Restart your Django server after creating the `.env` file
4. Check for typos in variable names
5. Make sure there are no spaces around the `=` sign in `.env` file 