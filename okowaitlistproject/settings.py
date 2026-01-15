import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ze#%b^7zbr!6wh_%qht3i57mkf*1ilb7^dgl5%ru+*gt#-qhnb')

# Automatically turns off DEBUG on Render
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]

CSRF_TRUSTED_ORIGINS = [
    'https://website-backend-3.onrender.com',
    'https://okoaiapplication.onrender.com'
]

# --- APPS & MIDDLEWARE ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'waitlistapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Essential for Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'okowaitlistproject.urls'
WSGI_APPLICATION = 'okowaitlistproject.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# --- DATABASE ---
# Uses PostgreSQL on Render, SQLite locally
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# --- STATIC FILES ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- EMAIL (RESEND API SETTINGS) ---
# Pull your key from PowerShell (local) or Render Dashboard (production)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')

if DEBUG:
    # Print to console locally so you don't waste your API limit
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # This is a placeholder; our views.py uses the Resend SDK directly
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Since you have no domain, you MUST use this address
DEFAULT_FROM_EMAIL = 'Oko <onboarding@resend.dev>'

# --- PRODUCTION SECURITY ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True