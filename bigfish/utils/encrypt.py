import datetime
import random

from cryptography.fernet import Fernet

change_key = Fernet.generate_key()
default_Key = b'HoJwNl4WyoHtE9hY4gvgj_ZIw1xf-1OBK-50giJjcHE='
BASE_LIST = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def encrypt(password, key=default_Key):
    ret_pwd = Fernet(key).encrypt(password.encode()).decode()
    return ret_pwd


def decrypt(password, key=default_Key):
    ret_pwd = Fernet(key).decrypt(password.encode()).decode()
    return ret_pwd


def convert_to_base_x(n, base=10):
    x, y = divmod(n, base)
    if x > 0:
        return convert_to_base_x(x, base) + BASE_LIST[y]
    else:
        return BASE_LIST[y]


def generate_serial_num():
    year_month = datetime.datetime.now().strftime('%y%m')
    random_data = str(random.randint(0, 99999)).zfill(5)
    serial_num = "{}{}".format(year_month, random_data)
    return int(serial_num)


if __name__ == '__main__':
    # pwd = 'bianhy123'
    # print(pwd)
    # pwd_en = encrypt(pwd)
    # print(pwd_en)
    # pwd_de = decrypt(pwd_en)
    # print(pwd_de)

    bb = convert_to_base_x(180900001, 32)
    print(bb)
