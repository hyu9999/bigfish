import logging

import psycopg2

logger = logging.getLogger('django')


# 主库
class BasicDB:
    DATABASES = {
        'default': {
            'name': 'bigfish_loc',
            'engine': 'django.db.backends.postgresql',
            'user': 'postgres',
            'port': '5433',
            'password': '111111',
        }

    }


# 备用库
class SpareDB:
    DATABASES = {
        'default': {
            'name': 'bigfish_touping',
            'engine': 'django.db.backends.postgresql',
            'user': 'postgres',
            'port': '5432',
            'host': '39.130.160.107',
            'password': 'mint@2016',
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
