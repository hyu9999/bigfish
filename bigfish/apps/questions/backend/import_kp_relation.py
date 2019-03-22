# coding=utf8
import logging

import xlrd
from django.db import transaction

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.questions.models import QuestionKPRelationship

logger = logging.getLogger('backend')


def main_func(file_path):
    # 打开文件
    workbook = xlrd.open_workbook(file_path)
    # # 根据sheet索引或者名称获取sheet内容
    sheet2 = workbook.sheet_by_index(0)  # sheet索引从0开始
    with transaction.atomic():
        for i in range(1, sheet2.nrows):
            data_list = sheet2.row_values(i)
            question_id, relations = data_list
            first_list = relations.split("&")
            for f_idx, first in enumerate(first_list):
                second_list = first.split("|")
                for s_idx, second in enumerate(second_list):
                    tmp_dict = {"order": f_idx + 1, "seconds": s_idx + 1, "question_id": int(question_id),
                                "knowledge_point_id": second}
                    QuestionKPRelationship.objects.create(**tmp_dict)


if __name__ == '__main__':
    main_func("知识点关系.xlsx")
