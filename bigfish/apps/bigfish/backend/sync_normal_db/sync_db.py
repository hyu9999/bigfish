import os
import sys

import psycopg2

DB_CONF = {
    "database": "bigfish2_bat",
    "user": "postgres",
    "password": "mint@2016",
    "host": "39.130.160.107",
    "port": "5432"
}


def conn_db():
    # 数据库连接参数
    conn = psycopg2.connect(**DB_CONF)
    return conn


def execute_sql_file(filename):
    conn = conn_db()
    cur = conn.cursor()
    with open(filename, 'rb') as fo:
        for line in fo:
            line = line.decode('utf-8').strip()
            if line:
                print("===[{}]".format(line))
                cur.execute(line)
    conn.commit()
    cur.close()
    conn.close()


def main_func():
    file_list = os.listdir("sql_dir")
    file_list.sort()
    print(file_list)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in file_list:
        sql_file = os.path.join(base_dir, 'sql_dir', filename)
        print("======================={}".format(sql_file))
        try:
            execute_sql_file(sql_file)
        except Exception as e:
            print("***********************{}".format(e))
            sys.exit(-2)


if __name__ == '__main__':
    # main_func()
    a = ['asdasd\nasdadsasda', 'asdads\ndasdas']
    for item in a:
        exec("b = item")
        print(b)
