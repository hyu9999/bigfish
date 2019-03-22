import os

from bigfish.settings.base import *  # noqa
# from bigfish.settings.db_config import MyConfig

ALLOWED_HOSTS = ['39.130.160.108','39.130.160.106', 'www.bigfishai.com', 'superfish.inketang.com']

STATIC_ROOT = '/home/www/bigfish_server/static'
MEDIA_ROOT = '/home/www/bigfish_server/media'
PACKAGE = '/home/www/bigfish_server'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': 'bigfish2',
       'USER':'postgres',
       'PASSWORD': '111111',
       'HOST': 'localhost'
    }
}
# SESSION_COOKIE_AGE = 2
SESSION_COOKIE_AGE = 60 * 60 * 12
# REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES = 1



AUTH_PASSWORD_VALIDATORS = []

