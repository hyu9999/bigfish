import time

import datetime


def check_in_time_range(start_time, end_time, my_time):
    flag = False
    if isinstance(start_time, datetime.datetime):
        start_time = datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
    start_time = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(end_time, datetime.datetime):
        end_time = datetime.datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S')
    end_time = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(my_time, datetime.datetime):
        my_time = datetime.datetime.strftime(my_time, '%Y-%m-%d %H:%M:%S')
    my_time = time.strptime(my_time, '%Y-%m-%d %H:%M:%S')
    if int(time.mktime(my_time)) in range(int(time.mktime(start_time)), int(time.mktime(end_time)) + 1):
        flag = True
    return flag


if __name__ == '__main__':
    s_time = "2018-03-01 00:00:00"
    e_time = "2018-03-01 20:00:00"
    m_time = "2018-03-01 20:00:00"
    f = check_in_time_range(s_time, e_time, m_time)
    print(f)
