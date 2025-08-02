import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-04e5xdoalt@b9z25p(uqa&!j!14j65yih9n!b_4q7lelybcy4z'

ALLOWED_HOSTS = ['*']

DEBUG = True

LOCAL_APPS = [
    'apps.accounts',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'corsheaders',
    'django_filters',
    'django_ckeditor_5',
    *LOCAL_APPS,
]

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    *THIRD_PARTY_APPS,
]

LOCAL_MIDDLEWARE = [
    'config.middleware.middleware.JsonErrorResponseMiddleware',
    'config.middleware.middleware.Custom404Middleware',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    *LOCAL_MIDDLEWARE,
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "/var/www/media/")

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
    "PAGE_SIZE": 100,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = True

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL = 'accounts.CustomUser'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vela',
        'USER': 'postgres',
        "PASSWORD": "0576",
        "HOST": "localhost",
        "PORT": 5432,
    }
}


SITE_ID = 1

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

# Facebook OAuth Settings
# FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
# FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
# FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "")

FACEBOOK_APP_ID=os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET=os.getenv("FACEBOOK_APP_SECRET", "")
FACEBOOK_REDIRECT_URI=os.getenv("FACEBOOK_REDIRECT_URI", "")

# External API Configuration
MEDITATION_API_CONFIG = {
    'BASE_URL': os.environ.get('MEDITATION_API_BASE_URL', 'http://31.97.98.47:9000'),
    'TIMEOUT': int(os.environ.get('MEDITATION_API_TIMEOUT', 10)),
    'ENABLED': os.environ.get('MEDITATION_API_ENABLED', 'True').lower() == 'true',
    'ENDPOINTS': {
        'sleep': '/sleep',
        'spark': '/spark',
        'calm': '/calm',
        'dream': '/dream'
    }
}

# Django server URL for file serving
DJANGO_SERVER_URL = os.environ.get('DJANGO_SERVER_URL', 'http://31.97.98.47:8080')

# External meditation API settings
EXTERNAL_MEDITATION_API_ENABLED = os.environ.get('EXTERNAL_MEDITATION_API_ENABLED', 'False').lower() == 'true'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'apps.accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}