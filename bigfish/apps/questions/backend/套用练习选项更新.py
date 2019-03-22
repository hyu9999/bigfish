# coding=utf8
import logging

import xlrd
from django.db import transaction

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.questions.models import Question

logger = logging.getLogger('backend')


def main_func(file_path):
    # 打开文件
    workbook = xlrd.open_workbook(file_path)
    # # 根据sheet索引或者名称获取sheet内容
    sheet2 = workbook.sheet_by_index(0)  # sheet索引从0开始
    with transaction.atomic():
        for i in range(1, sheet2.nrows):
            data_list = sheet2.row_values(i)
            question_id, options = data_list
            logger.info("update {} [{}]".format(question_id, options))
            Question.objects.update_or_create(defaults={"options": options}, id=int(question_id))


if __name__ == '__main__':
    main_func("套用练习题ID.xlsx")
