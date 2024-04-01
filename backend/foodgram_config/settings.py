from pathlib import Path
import os
# from decouple import config


DATE_TIME_FORMAT = "%d/%m/%Y %H:%M"

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-cg6*%6d51ef8f#4!r3*$vmxm4)abgjw8mo!4y-q*uq1!4$-89$'
SECRET_KEY = 'd5071bea3ec8160a9bf6a50f7a46f72834f83c0e'

# DEBUG = True
DEBUG = False

# ALLOWED_HOSTS = ['51.250.25.35', 'food-contact.online']
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    "https://51.250.25.35",
    "https://food-contact.online",
    "http://localhost:8080",
    "http://127.0.0.1:8000"
]

ROOT_URLCONF = "foodgram_config.urls"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'djoser',
    'corsheaders',
    'foodgram_api.apps.FoodgramApiConfig',
    'users.apps.UsersConfig',
    'reviews.apps.ReviewsConfig'
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
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'test_database'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default="postgres"),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}
AUTH_USER_MODEL = "users.FoodUser"

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

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": False,
    "PERMISSIONS": {
        # 'resipe': ("foodgram_api.permissions.IsAuthenticated,",),
        # 'recipe_list': ("foodgram_api.permissions.AllowAny",),
        'user': ("foodgram_api.permissions.IsAuthenticated",),
        'user_list': ("foodgram_api.permissions.AllowAny",),
        'subscribe': ("foodgram_api.permissions.IsAuthenticated",),
        'subscriptions': ("foodgram_api.permissions.IsAuthenticated",),
        'shopping_cart': ("foodgram_api.permissions.IsAuthenticated,",)
    },
}

LANGUAGE_CODE = "ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
USE_L10N = True


MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = BASE_DIR / MEDIA_URL

STATIC_URL = '/static/'
#STATIC_ROOT = BASE_DIR / 'static'
# STATIC_ROOT = BASE_DIR / 'staticfiles' 'collected_static'
STATIC_ROOT = BASE_DIR / 'static'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
