import datetime
import os
import platform
import stat

from pathlib import Path

from bigfish.settings.db_config import MyConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = 'bigfish'
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1(d58ti3kx_zoux#s7fz_m_3l^6r0p_i#o!zc%v#vtx6!*--s3'
from corsheaders.defaults import default_headers

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

APPEND_SLASH = True
AUTH_USER_MODEL = "users.BigfishUser"
INSTALLED_APPS = [

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'import_export',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'ajax_select',
    'corsheaders',
    'simple_sso.sso_server',

    # 'channels'
    'bigfish.apps.auth',
    'bigfish.apps.bigfish',
    'bigfish.apps.achievement',
    'bigfish.apps.areas',
    'bigfish.apps.attention',
    'bigfish.apps.bfwechat',
    'bigfish.apps.classrooms',
    'bigfish.apps.collection',
    'bigfish.apps.contents',
    'bigfish.apps.dubbing',
    'bigfish.apps.homework',
    'bigfish.apps.impactassessment',
    'bigfish.apps.integral',
    'bigfish.apps.intelligentpush',
    'bigfish.apps.knowledgepoint',
    'bigfish.apps.operation',
    'bigfish.apps.overall',
    'bigfish.apps.public',
    'bigfish.apps.questions',
    'bigfish.apps.reports',
    'bigfish.apps.research',
    'bigfish.apps.schools',
    'bigfish.apps.shops',
    'bigfish.apps.resources',
    'bigfish.apps.teachingfeedback',
    'bigfish.apps.textbooks',
    'bigfish.apps.users',
    'bigfish.apps.versionupdate',
    'bigfish.apps.versus',
    'bigfish.apps.visualbackend',
    'bigfish.apps.voice',
    'bigfish.apps.xiwo',
    'bigfish.apps.wrongtopic',
    "bigfish.utils",
    'django.contrib.admin',

]

# 主题
JET_THEMES = [
    {
        'theme': 'default',  # theme folder name
        'color': '#47bac1',  # color of the theme's button in user menu
        'title': 'Default'  # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]
SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ['rest_framework_swagger', ]
    SWAGGER_SETTINGS = {
        # 基础样式
        'SECURITY_DEFINITIONS': {
            "basic": {
                'type': 'basic'
            }
        },
        # 如果需要登录才能够查看接口文档, 登录的链接使用restframework自带的.
        'LOGIN_URL': 'rest_login',
        'LOGOUT_URL': 'rest_framework:logout',
        # 'DOC_EXPANSION': None,
        # 'SHOW_REQUEST_HEADERS':True,
        # 'USE_SESSION_AUTH': True,
        # 'DOC_EXPANSION': 'list',
        # 接口文档中方法列表以首字母升序排列
        'APIS_SORTER': 'alpha',
        # 如果支持json提交, 则接口文档中包含json输入框
        'JSON_EDITOR': False,
        # 方法列表字母排序
        'OPERATIONS_SORTER': 'alpha',
        'VALIDATOR_URL': None,
    }
ROOT_URLCONF = 'bigfish.apps.bigfish.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "bigfish/apps/bfwechat/templates/",
            "bigfish/apps/bigfish/templates/"
        ],
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

WSGI_APPLICATION = 'bigfish.apps.bigfish.wsgi.application'

my_config = MyConfig()
DATABASES = my_config.get_config()

# DATABASES = {
# 'default': {
# 'NAME': 'bigfish2',
# 'ENGINE': 'django.db.backends.postgresql',
# 'USER': 'postgres',
# 'PORT': '5432',
# 'HOST': "39.130.160.107",
# 'PASSWORD': 'mint@2016'
# },
# }
CACHES = {
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #     'LOCATION': '127.0.0.1:11211',
    # },
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        "OPTIONS": {
            # "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CLIENT_CLASS": "django_redis.client.HerdClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 2}
            # "PASSWORD": "mysecret",
            # "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            # "SOCKET_TIMEOUT": 5,  # in seconds
        }
    },
    # this cache backend will be used by django-debug-panel
    'debug-panel': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'debug-panel-cache'),
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 200
        }
    }
}
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False

USE_L10N = False
DATETIME_FORMAT = 'Y-m-d H:i:s'
DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i:s'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DOC_DIR = os.path.join(BASE_DIR, 'docs')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'docs'),
#     os.path.join(BASE_DIR, 'static'),
# ]
# DEFAULT_FILE_STORAGE = 'bigfish.utils.bf_storage.FileSystemStorage'
# default_storage = 'bigfish.utils.bf_storage.FileSystemStorage'
DEFAULT_PAGINATION_CLASS = 'bigfish.base.pagination.BFPageNumberPagination'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'bigfish.authentication.CrsfExemptSessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    # 分页规则设置
    'DEFAULT_PAGINATION_CLASS': DEFAULT_PAGINATION_CLASS,
    'PAGE_SIZE': 100,
    # 限流规则设置
    # 'DEFAULT_THROTTLE_CLASSES': (
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle'
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '2/m',
    #     'user': '3/m'
    # }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# allauth specific settings
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    # 'guardian.backends.ObjectPermissionBackend',
)

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'bigfish.apps.auth.serializers.RegisterSerializer',
}
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

try:
    from local_settings import *  # NOQA
except ImportError:
    pass

CORS_ORIGIN_ALLOW_ALL = True

PASSWORD_HASHERS = ('bigfish.utils.hashers.PlainTextPassword',)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ================== log 配置 ==================
# 指定日志根目录
if platform.system() == 'Linux':
    LOG_BASE_PATH = '/home/www/logs/project/{}'.format(PROJECT_NAME)
elif platform.system() == 'Windows':
    LOG_BASE_PATH = r'd:\Python\bigfish\trunk\log'
else:
    LOG_BASE_PATH = ''
# 指定日志文件
LOG_FILE = os.path.join(LOG_BASE_PATH, 'web', 'log')  # web日志路径
LOG_FILE_BACKEND = os.path.join(LOG_BASE_PATH, 'backend', 'log')  # 后台日志路径

# ================== log 配置 ==================
# 日志级别控制
LOG_LEVEL = 'DEBUG'
BACKEND_LOG_LEVEL = 'INFO'
# 指定日志根目录
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(name)s:%(filename)s:%(lineno)d][%(levelname)-8s] %(message)s'
        },
        'backend': {
            'format': '%(asctime)s [%(name)s:%(pathname)s:%(lineno)d][%(levelname)-8s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE,
            'formatter': 'standard'
        },
        'backend_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE_BACKEND,
            'formatter': 'backend'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_handler'],
            'level': LOG_LEVEL,
        },
        'backend': {
            'handlers': ['console', 'file_handler'],
            'level': BACKEND_LOG_LEVEL,
            'propagate': True,
        }
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
        "ROUTING": "bigfish.settings.routing.channel_routing",
    },
}

WECHAT_APPID = "wx923f6e5c3b4d4f08"
WECHAT_APPSECRET = "cae9316aa364648f635ccf3e1170f49a"
WECHAT_TOKEN = "superfish2018"
CASH_TIME = 7200
WEHOST = "http://flyingcloud.com.cn"

WX_WECHAT_APPID = "wxe083dfd04f3ba126"
WX_WECHAT_APPSECRET = "d45ac0a94ca0107af438b7a28c12379f"
SSO_SERVER = "http://49.4.7.114:8000/server/"  # 服务器地址
SSO_PUBLIC_KEY = "mYmVwelbg7Pnt19ATYbx53kLhuwLIPPLBgTUjwIcSxcwCHb3FVUVU21GNWBlh65F"  # 公钥
SSO_PRIVATE_KEY = "jFaALg8S3owcIlm40jCZSf6cJhoBz9ZCIPRPy9oKOaGO2IT1UPomY1G7Ppznkz4W"  # 密钥
