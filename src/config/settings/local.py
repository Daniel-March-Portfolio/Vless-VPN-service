import os

from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q^!l7xvlm(92ae9_+a@=!5l-=jj0sm1cp$yokm*)$xnzs1vqf$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

HOST = 'https://127.0.0.1:8000'
ALLOWED_HOSTS = ['127.0.0.1']
KEYS_ROOT_DOMAIN = 'example.com'
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

BOT_TOKEN = os.getenv('BOT_TOKEN') or '0:0'
REDIS_CONNECTION_STRING = 'redis://redis:6379/0'
BOT_WEBHOOK = None
DOMAIN = None

STATIC_ROOT = BASE_DIR / 'static'
