# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1(d58ti3kx_zoux#s7fz_m_3l^6r0p_i#o!zc%v#vtx6!*--s3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

from bigfish.settings.base import *  # NOQA

AUTH_PASSWORD_VALIDATORS = []
app_key, master_secret = 'c6cb8d96a10a6fb06981bb0b', 'd4ccf75caa90e9b6f75a6c22'
#亚马逊的Key：
# AWSAccessKeyId=AKIAJRBNGPM64F3W23SQ
# AWSSecretKey=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
# us-east-2