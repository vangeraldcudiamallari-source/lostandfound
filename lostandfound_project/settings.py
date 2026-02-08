"""
Django settings for lostandfound_project project.
Updated for Django 5.2+ with Brutalist Tailwind support.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECURITY SETTINGS
# --------------------------------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev')
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
INSTALLED_APPS = [
    # Local Apps
    'core',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third Party Apps
    'crispy_forms',
    'crispy_tailwind',
    'widget_tweaks',
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------------
# URL CONFIG
# --------------------------------------------------
ROOT_URLCONF = 'lostandfound_project.urls'

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # Essential for accessing profile images in templates
                'core.context_processors.unread_messages_count',
            ],
        },
    },
]

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC & MEDIA FILES
# --------------------------------------------------
STATIC_URL = '/static/'
PROJECT_STATIC_DIR = BASE_DIR / "static"
PROJECT_STATIC_DIR.mkdir(exist_ok=True) 

STATICFILES_DIRS = [PROJECT_STATIC_DIR]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media configuration for User Identity (Avatars/Images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Ensure directory exists for system uploads
MEDIA_ROOT.mkdir(exist_ok=True)

# --------------------------------------------------
# AUTH SETTINGS
# --------------------------------------------------
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:dashboard' # Redirecting to dashboard after login is usually preferred
LOGOUT_REDIRECT_URL = 'core:home'

# --------------------------------------------------
# EMAIL SETTINGS (Brutalist System Update)
# --------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'geraldcudia19@gmail.com' 
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', 'dqzpdnqcyxftvzxz').strip()

# Brutalist Transmission Identity
DEFAULT_FROM_EMAIL = 'FOUND.IT SYSTEMS <geraldcudia19@gmail.com>'

# --------------------------------------------------
# CRISPY FORMS CONFIGURATION
# --------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'