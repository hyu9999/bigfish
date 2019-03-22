import logging

import psycopg2

logger = logging.getLogger('django')


# 主库
class BasicDB:
    DATABASES = {
        'default': {
            'NAME': 'bigfish',
            'ENGINE': 'django.db.backends.postgresql',
            'USER': 'postgres',
            'PORT': '5432',
            'HOST': 'localhost',
            'PASSWORD': '111111',
        }

    }


# 备用库
class SpareDB:
    DATABASES = {
        'default': {
            'NAME': 'bigfish',
            'ENGINE': 'django.db.backends.postgresql',
            'USER': 'postgres',
            'PORT': '5432',
            'HOST': 'localhost',
            'PASSWORD': '111111',
        }
    }


class MyConfig:
    __conf = None

    @staticmethod
    def check_conn(**param):
        flag = False
        try:
            param = {"database": param.get("name", None), "user": param.get("user", None),
                     "password": param.get("password", None), "host": param.get("host", None),
                     "port": param.get("port", None)
                     }
            conn = psycopg2.connect(**param)
        except Exception as e:
            logger.info("基础库连接异常【{}】".format(e))
            pass
        else:
            conn.close()
            flag = True
        return flag

    def get_config(self):
        config_info = BasicDB().DATABASES.get("default", None)
        flag = self.check_conn(**config_info)
        if flag:
            logger.error("当前数据库【BasicDB】")
            self.__conf = BasicDB()
        else:
            logger.error("当前数据库【SpareDB】")
            self.__conf = SpareDB()
        return self.__conf.DATABASES
