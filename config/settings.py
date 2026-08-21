from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost'
).split(',')

# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django REST Framework
    'rest_framework',
    'rest_framework.authtoken',

    # Наши приложения
    'users',
    'products',
    'cart',
    'orders',
    'favorites',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# =========================================================
# LANGUAGE / TIME
# =========================================================

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC
# =========================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# =========================================================
# MEDIA
# =========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# LOGIN / LOGOUT
# =========================================================

LOGIN_URL = 'users:login'

LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'home'


# =========================================================
# DJANGO REST FRAMEWORK + JWT
# =========================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        (
            'rest_framework_simplejwt.authentication.'
            'JWTAuthentication'
        ),
        (
            'rest_framework.authentication.'
            'SessionAuthentication'
        ),
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        (
            'rest_framework.permissions.'
            'IsAuthenticatedOrReadOnly'
        ),
    ],
}