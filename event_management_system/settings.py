from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-q0-!6c4228evgasyo%nl828#-p*a+yr(bw!8znp-!+vfgv3@yf'
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'events',
    'storages',

]

# AWS settings
AWS_ACCESS_KEY_ID = 'AKIAQPHJMQZMHM5IM7J2'
AWS_SECRET_ACCESS_KEY = 'BStS5Ga1VYf/gygrOzXXOjtPxLyfAB9Eet9bGZi1'
AWS_STORAGE_BUCKET_NAME = 'eventhub-storage'
AWS_S3_REGION_NAME = 'eu-north-1'  # e.g., 'us-east-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'

# S3 bucket configuration
AWS_S3_CUSTOM_DOMAIN = f'eventhub-storage.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# # Static files (CSS, JavaScript, images)
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

# Media files (uploads)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Optional: If you have static files locally
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = '/'  # URL to redirect to after successful login
LOGOUT_REDIRECT_URL = '/'  # URL to redirect to after logout

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'event_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'events', 'templates', 'events')],  # Ensure this path is correct
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

WSGI_APPLICATION = 'event_management_system.wsgi.application'

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eventhub_database',
        'USER': 'alvin',
        'PASSWORD': 'acEKFodfmwBp9TXCcfVtpVFPWkb1e4ep',
        'HOST': 'dpg-cqppp8dsvqrc7380dsa0-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# # Media files
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'alvinksabu200115@gmail.com'
EMAIL_HOST_PASSWORD = 'ceoj dbha miri hkdw'

