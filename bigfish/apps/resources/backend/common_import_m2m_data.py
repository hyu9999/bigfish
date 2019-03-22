import os
import sys

import xlrd
from django.db import transaction

from bigfish.utils.django.config_settings import config_django

config_django()

import logging

logger = logging.getLogger('backend')


def list_folder():
    """
    遍历文件夹

    :return:
    """
    ret_data = []
    for filename_ext in os.listdir('data/m2m'):
        filename = filename_ext.split(".")[0]
        tmp_data = filename.split("-")[1:]
        file_path = "{}/{}/{}".format(os.path.dirname(__file__), 'data/m2m', filename_ext)
        tmp_data.append(file_path)
        ret_data.append(tmp_data)
    return ret_data


def import_excel(app_name, model_name, m2m, filename):
    exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
    try:
        print(exec_str)
        exec(exec_str)
    except Exception as e:
        logger.debug(e)
        sys.exit(-1)
    sql_list = get_excel_data(app_name, model_name, m2m, filename, "Sheet1")
    try:
        ret_queryset = eval("{0}.{1}.through.objects.bulk_create(sql_list)".format(model_name, m2m))
    except Exception as e:
        logger.error(e)
        sys.exit(-4)
    return ret_queryset


def get_excel_data(app_name, model_name, m2m, path, sheet_name):
    exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
    try:
        print(exec_str)
        exec(exec_str)
    except Exception as e:
        logger.debug(e)
        sys.exit(-1)
    bk = xlrd.open_workbook(path)
    sh = bk.sheet_by_name(sheet_name)
    row_num = sh.nrows
    data_list = []
    for i in range(1, row_num):
        row_data = sh.row_values(i)
        if "," in str(row_data[1]):
            second_data = [str(x) for x in row_data[1].split(",")]
            print(second_data)
            for item in second_data:
                data_dict = dict(zip(sh.row_values(0), [sh.row_values(i)[0], item]))
                data_str = "{0}.{1}.through(**{2})".format(model_name, m2m, data_dict)
                data = eval(data_str)
                data_list.append(data)
        else:
            data_dict = dict(zip(sh.row_values(0), sh.row_values(i)))
            data_str = "{0}.{1}.through(**{2})".format(model_name, m2m, data_dict)
            print(data_str)
            data = eval(data_str)
            data_list.append(data)
    print(data_list)
    return data_list


def main_func():
    """
    主函数
        m2m = TextbookWord.image.through(textbookword_id=textbookword_id, image_id=image_id)
        m2m_list.append(m2m)
        TextbookWord.image.through.objects.bulk_create(m2m_list)
    :return:
    """
    file_list = list_folder()
    with transaction.atomic():
        for item in file_list:
            logger.debug("start import==========================================={}".format(item))
            import_excel(*item)
            logger.debug("end import==========================================={}".format(item))


if __name__ == '__main__':
    main_func()
