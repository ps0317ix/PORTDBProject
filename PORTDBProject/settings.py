import os
import datetime
import platform
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

SLACK_URL = 'https://hooks.slack.com/services/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'


# ALLOWED_HOSTS = [
#     'localhost',
#     '127.0.0.1',
#     '160.251.3.51',
#     '18.179.120.144',
#     '54.250.3.223',
#     '.ngrok.io',
#     'master-server.ap.ngrok.io',
#     '8d54-116-80-72-245.jp.ngrok.io',
#     '.web.app',
# ]
ALLOWED_HOSTS = ['*']

# CORS関連
CORS_ORIGIN_WHITELIST = (
    'http://localhost:4040',
    'http://127.0.0.1:4040',
    'http://localhost:4041',
    'http://127.0.0.1:4041',
    'http://localhost:9520',
    'http://127.0.0.1:9520'
)

CORS_Origin_REGEX_WHITELIST = [
    'http://localhost:4040',
    'http://127.0.0.1:4040',
    'http://localhost:4041',
    'http://127.0.0.1:4041',
    'http://localhost:9520',
    'http://127.0.0.1:9520'
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4040',
    'http://127.0.0.1:4040',
    'http://localhost:4041',
    'http://127.0.0.1:4041',
    'http://localhost:9520',
    'http://127.0.0.1:9520'
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'user',
    'contact',
    'sendContent',
    'sendDM',
    'sender',
    'server',
    'receiveDM',
    'rest_framework',
    'dbbackup',
    'storages',
    'health_check',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.psutil',
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'PORTDBProject.urls'

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

WSGI_APPLICATION = 'PORTDBProject.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ja-JP'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True
USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user.User'

# JWTの認証追加
JWT_AUTH = {
    # トークンの期限をここでは無効にしてみる
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=6600),
}

REST_FRAMEWORK = {
    # ページネーションの設定
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.LimitOffsetPagination'
    ),
    # JWTの認証設定
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'NON_FIELD_ERRORS_KEY': 'detail',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,    # in MB
}

# ローカル環境の設定を読み込む
if platform.system() != 'Linux':
    from .local_settings import *

    DATABASES = {
        # AWS 開発用DB
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'port',
            'USER': 'konome',
            'PASSWORD': 'konomekonomekonome007',
            'HOST': 'port.c1qearomhtyp.ap-northeast-1.rds.amazonaws.com',
            'PORT': '5432',
        }
    }
    # GKE DB
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': os.getenv('DATABASE_NAME'),
    #         'USER': os.getenv('DATABASE_USER'),
    #         'PASSWORD': os.getenv('DATABASE_PASSWORD'),
    #         'HOST': '127.0.0.1',
    #         'PORT': '5432',
    #     }
    # }

else:
    # SECURITY WARNING: don't run with debug turned on in production!
    # DEBUG = False
    DEBUG = True
    SECRET_KEY = 'django-insecure-hv6=2)yxoutjsypki1%fy%5puhas1_%%vofb##9y!npb_69q5u'
    # GKE DB
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': os.getenv('DATABASE_NAME'),
    #         'USER': os.getenv('DATABASE_USER'),
    #         'PASSWORD': os.getenv('DATABASE_PASSWORD'),
    #         'HOST': '127.0.0.1',
    #         'PORT': '5432',
    #     }
    # }
    DATABASES = {
        # AWS 開発用DB
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'port',
            'USER': 'konome',
            'PASSWORD': 'konomekonomekonome007',
            'HOST': 'port.c1qearomhtyp.ap-northeast-1.rds.amazonaws.com',
            'PORT': '5432',
        }
    }

db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
DATABASES['default'].update(db_from_env)

STATIC_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/nginx/static'

# DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
# DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backups')}
DBBACKUP_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
DBBACKUP_STORAGE_OPTIONS = {"bucket_name": "superb-leaf-313807_port"}

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

AWS_ACCESS_KEY_ID = 'AKIA3F3VDIG35FQD5SA6'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'port-s3'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_DEFAULT_ACL = None
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_FILE_STORAGE = 'localupload.storage_backends.MediaStorage'
