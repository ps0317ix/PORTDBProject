import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'django-insecure-hv6=2)yxoutjsypki1%fy%5puhas1_%%vofb##9y!npb_69q5u'

# SQLite3 DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'PORTDBProject.sqlite3'),
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

DEBUG = True
