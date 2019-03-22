import json
import os
import sys
import logging
import xlrd
from django.db import transaction

from bigfish.utils.django.config_settings import config_django

config_django()

logger = logging.getLogger('backend')
"""
1.多对多关系无法直接导入，删掉那一列(单独弄一组excel)
2.数字格式默认值为0，不能写null
3.json格式默认值为{}，不能写null
4.字符串格式默认值不填，最好不要写null
5.id以及外键默认值可以填写None或者null
"""


def list_folder():
    """
    遍历文件夹

    :return:
    """
    ret_data = []
    for filename_ext in os.listdir('data'):
        if not os.path.isfile(os.path.join(os.path.dirname(__file__), 'data', filename_ext)):
            print(os.path.join(os.path.dirname(__file__), 'data', filename_ext))
            continue
        filename = filename_ext.split(".")[0]
        tmp_data = filename.split("-")[1:]
        file_path = "{}/{}/{}".format(os.path.dirname(__file__), 'data', filename_ext)
        tmp_data.append(file_path)
        ret_data.append(tmp_data)
    return ret_data


def import_data(app_name, model_name, url_path):
    """
    导入数据（单文件）

    :param app_name:
    :param model_name:
    :param url_path:
    :return:
    """
    exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
    try:
        exec(exec_str)
    except Exception as e:
        logger.debug(e)
        sys.exit(-1)
    try:
        eval('import_excel({0},url_path)'.format(model_name, url_path))
    except Exception as e:
        logger.debug('导入错误：{}'.format(e))
        sys.exit(-2)


def import_excel(model_obj, filename):
    with transaction.atomic():
        bk = xlrd.open_workbook(filename)
        sh = bk.sheet_by_name("Sheet1")
        row_num = sh.nrows
        for i in range(1, row_num):
            row_data = sh.row_values(i)
            tmp_data = {}
            for index, key in enumerate(sh.row_values(0)):
                if key in ['purpose', 'step', 'task', 'statement', 'rule', 'knowledge_point']:
                    if row_data[index] == 'null':
                        row_data[index] = {}
                    else:
                        try:
                            data = row_data[index]
                            row_data[index] = json.loads(data)
                        except Exception as e:
                            logger.error("[json error][{}][{}]{}".format(i, row_data, e))
                            sys.exit(-7)
                if row_data[index] == 'null':
                    row_data[index] = None
                elif row_data[index] == '#N/A':
                    break
                tmp_data[key] = row_data[index]
            print("{}========================={}".format(i, tmp_data))
            try:
                model_obj.objects.update_or_create(defaults=tmp_data, **{"id": int(tmp_data['id'])})
            except Exception as e:
                logger.error(e)
                sys.exit(-6)


def main_func():
    """
    主函数

    :return:
    """
    file_list = list_folder()
    with transaction.atomic():
        for item in file_list:
            logger.debug("start import==========================================={}".format(item))
            import_data(*item)
            logger.debug("end import==========================================={}".format(item))


if __name__ == '__main__':
    main_func()
