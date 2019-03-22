import os

from bigfish.settings.base import *  # noqa

ALLOWED_HOSTS = ['chatii.chatbao.com']

STATIC_ROOT = '/opt/server/static'
MEDIA_ROOT = '/opt/server/media'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': os.environ['POSTGRES_DB'],
       'USER': os.environ['POSTGRES_USER'],
       'PASSWORD': os.environ['POSTGRES_PASSWORD'],
       'HOST': 'postgres'
    }
}

AUTH_PASSWORD_VALIDATORS = []
