from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = (os.getenv('SECRET_KEY'))

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(', ')

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(', ')

ROOT_URLCONF = 'foodgram_config.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'django_filters',
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

AUTH_USER_MODEL = 'users.FoodUser'

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
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'SEARCH_PARAM': 'name',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}

# DJOSER = {
#     'LOGIN_FIELD': 'email',
#     'HIDE_USERS': False,
#     'PERMISSIONS': {
#         'resipe': ('foodgram_api.permissions.IsAuthenticated,',),
#         'recipe_list': ('foodgram_api.permissions.AllowAny',),
#         'user': ('foodgram_api.permissions.AuthorStaffOrReadOnly',),
#         'user_list': ('foodgram_api.permissions.AllowAny',),
#         'subscribe': ('foodgram_api.permissions.IsAuthenticated',),
#         'subscriptions': ('foodgram_api.permissions.IsAuthenticated',),
#         'shopping_cart': ('foodgram_api.permissions.IsAuthenticated,',)
#     },
# }
DJOSER = { 

    "LOGIN_FIELD": "email", 

    "HIDE_USERS": False, 

    "PERMISSIONS": { 

        'resipe': ("foodgram_api.permissions.IsAuthenticated,",), 

        'recipe_list': ("foodgram_api.permissions.AllowAny",), 

        'user': ("foodgram_api.permissions.AuthorStaffOrReadOnly",), 

        'user_list': ("foodgram_api.permissions.AllowAny",), 

        'subscribe': ("foodgram_api.permissions.IsAuthenticated",), 

        'subscriptions': ("foodgram_api.permissions.IsAuthenticated",), 

        'shopping_cart': ("foodgram_api.permissions.IsAuthenticated,",) 

    }, 

}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
USE_L10N = True


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / MEDIA_URL

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
