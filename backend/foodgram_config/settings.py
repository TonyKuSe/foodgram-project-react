from pathlib import Path
import os
# from decouple import config


DATE_TIME_FORMAT = "%d/%m/%Y %H:%M"

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-cg6*%6d51ef8f#4!r3*$vmxm4)abgjw8mo!4y-q*uq1!4$-89$'

DEBUG = True
ALLOWED_HOSTS = []
# ALLOWED_HOSTS = ['198.211.99.20', 'localhost', '127.0.0.1', 'backend']

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
    'foodgram_api.apps.FoodgramApiConfig',
    'users.apps.UsersConfig',
    'reviews.apps.ReviewsConfig'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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

# DATABASES = {
#     'default': {
#         # Меняем настройку Django: теперь для работы будет использоваться
#         # бэкенд postgresql
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'django'),
#         'USER': os.getenv('POSTGRES_USER', 'django'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', ''),
#         'PORT': os.getenv('DB_PORT', 5432)
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # "NAME": os.getenv("DB_NAME", default="postgres"),
        'NAME': 'test_database',
        'USER': 'postgres',
        # "USER": os.getenv("POSTGRES_USER", default="postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="postgres"),
        "HOST": os.getenv("DB_HOST", default=''),
        "PORT": os.getenv("DB_PORT", default=5432),
    }
}

AUTH_USER_MODEL = "users.FoodUser"

# AUTH_PASSWORD_VALIDATORS = [

#     {
#         "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
#     },

# ]
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
        # "rest_framework.permissions.IsAuthenticatedOrReadOnly",
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2,
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": False,
    "PERMISSIONS": {
        "resipe": ("foodgram_api.permissions.IsAuthenticated,",),
        "recipe_list": ("foodgram_api.permissions.AuthorStaffOrReadOnly",),
        "user": ("foodgram_api.permissions.OwnerUserOrReadOnly",),
        'user_list': ("foodgram_api.permissions.OwnerUserOrReadOnly",),
        'subscribe': ("foodgram_api.permissions.OwnerUserOrReadOnly",),
        'shopping_cart': ("foodgram_api.permissions.IsAuthenticated,",)
    },
    # "SERIALIZERS": {
    #     'user': 'users.serializers.UserSerializer',
    #     'current_user': 'users.serializers.UserMeSerializer',
    #     'user_create': 'users.serializers.UserSerializer',
    #     'set_password': 'users.serializers.UserSetPasswordSerializer',
    #     'password_reset': 'users.serializers.UserSetPasswordSerializer',
    #     'subscriptions': 'users.serializers.UserSerializer',
    # },
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
# STATIC_ROOT = BASE_DIR / 'static'
STATIC_ROOT = BASE_DIR / 'collected_static'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
