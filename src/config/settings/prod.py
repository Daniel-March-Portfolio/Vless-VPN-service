import os

from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

HOST = os.environ['HOST']
ALLOWED_HOSTS = list(os.environ['ALLOWED_HOSTS'].split(',')) + ['web.telegram.org']
CSRF_TRUSTED_ORIGINS = [f'https://{ALLOWED_HOST}' for ALLOWED_HOST in ALLOWED_HOSTS]

BOT_WEBHOOK = None
KEYS_ROOT_DOMAIN = os.environ['KEYS_ROOT_DOMAIN']
DOMAIN = os.environ['DOMAIN']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ['DATABASE_NAME'],
        "USER": os.environ["DATABASE_USER"],
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": os.environ["DATABASE_HOST"],
        "PORT": os.environ["DATABASE_PORT"],
    }
}

REDIS_CONNECTION_STRING = os.environ['REDIS_CONNECTION_STRING']
BOT_TOKEN = os.environ['BOT_TOKEN']

STATIC_ROOT = '/app/static'