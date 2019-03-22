# coding=utf8
import logging
import sys

import xlrd
from django.db import transaction

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.textbooks.models import Unit, Textbook
from bigfish.apps.knowledgepoint.models import KnowledgePoint

logger = logging.getLogger('backend')


def main_func(file_path):
    """
    更新知识点表(增删改)

    表头格式：
        编码      操作      名称  根节点名称  根节点编码       层级  排序   是否包含子节点   是否课标              单元  描述
        coding   operate  name  root      parent_code   level order has_children  curriculum_standard unit  desc

    操作符说明:
        ADD     新增
        UPDATE  更新
        DELETE  删除
        NO      跳过

    :param file_path:
    :return:
    """
    # 打开文件
    workbook = xlrd.open_workbook(file_path)
    # 根据sheet索引或者名称获取sheet内容
    sheets_list = workbook.sheet_names()
    sheet_num = len(sheets_list)

    for j in range(sheet_num):
        sheet = workbook.sheet_by_index(j)  # sheet索引从0开始
        with transaction.atomic():
            for i in range(1, sheet.nrows):
                # 读取一行内容
                data_list = sheet.row_values(i)
                coding, operate, name, root, parent_code, level, order, has_children, curriculum_standard, unit, desc = data_list
                print(coding, operate, name, root, parent_code, level, order, has_children, curriculum_standard, unit,
                      desc)
                # 判断操作
                fmt_operate = str(operate).upper()
                # 不在范围内的操作直接跳过
                if fmt_operate not in ['ADD', 'UPDATE', 'DELETE']:
                    continue
                # 删除操作则直接删除
                if fmt_operate == 'DELETE':
                    if not coding:
                        print("\n")
                        print("*" * 50)
                        print("[{}]删除操作必须传入编码！".format(i))
                        print("*" * 50)
                        sys.exit(-1)
                    KnowledgePoint.objects.filter(coding=coding).delete()
                else:
                    has_children = fmt_data(has_children)
                    curriculum_standard = fmt_data(curriculum_standard)
                    if fmt_operate == 'UPDATE':
                        kwargs = {"coding": coding}

                        defaults = {"name": name, "root": root, "level": level, "order": order,
                                    "has_children": has_children, "curriculum_standard": curriculum_standard,
                                    "desc": desc}
                        if parent_code:
                            defaults['parent_code'] = parent_code
                        obj, flag = KnowledgePoint.objects.update_or_create(defaults=defaults, **kwargs)
                        add_unit(unit, obj)

                    elif fmt_operate == 'ADD':
                        kwargs = {"name": name, "root": root, "parent_code": parent_code, "level": level,
                                  "order": order,
                                  "has_children": has_children, "curriculum_standard": curriculum_standard,
                                  "desc": desc}
                        new_obj = KnowledgePoint.objects.create(**kwargs)
                        add_unit(unit, new_obj)
                    else:
                        continue


def add_unit(unit, kp_obj):
    if unit:
        unit_list = get_unit_list(unit)
    else:
        unit_list = []
    kp_obj.unit.clear()
    for unit_obj in unit_list:
        kp_obj.unit.add(unit_obj)


def fmt_data(src):
    if not src or str(src).replace(" ", "") == "":
        flag = False
    else:
        flag = True
    return flag


def get_brother_knowledge(last_data, level):
    parent_code = last_data.parent_code
    try:
        parent_data = KnowledgePoint.objects.get(coding=parent_code)
    except Exception as e:
        logger.error(e)
        return False
    if parent_data.level > level:
        data = get_brother_knowledge(parent_data, level)
        if data.level == level:
            return data
    else:
        return parent_data


def get_unit_list(unit_str):
    GRADE_CHOICES = (
        (1, "小学一年级"),
        (2, "小学二年级"),
        (3, "小学三年级"),
        (4, "小学四年级"),
        (5, "小学五年级"),
        (6, "小学六年级"),
    )
    TERM_CHOICE = (
        ('上册', 'A'),
        ('下册', 'B'),
    )
    unit_list = unit_str.split("|")
    ret_list = []
    for unit_str in unit_list:
        if unit_str.startswith('PEP'):
            publish_id = 1
            try:
                grade = [y for (x, y) in GRADE_CHOICES if x == int(unit_str[3:4])][0]
            except Exception as e:
                logger.error(e)
                continue
            try:
                term = [x for (x, y) in TERM_CHOICE if y == unit_str[4:5]][0]
            except Exception as e:
                logger.error(e)
                continue
        elif unit_str.startswith('精通'):
            publish_id = 2
            try:
                grade = [y for (x, y) in GRADE_CHOICES if x == int(unit_str[2:3])][0]
            except Exception as e:
                logger.error(e)
                continue
            try:
                term = [x for (x, y) in TERM_CHOICE if y == unit_str[3:4]][0]
            except Exception as e:
                logger.error(e)
                continue
        else:
            continue

        bookgrade = '{}{}'.format(grade, term)
        tb = Textbook.objects.get(publish_id=publish_id, bookgrade=bookgrade)
        title = "Unit {}".format(unit_str[-1])
        try:
            obj = Unit.objects.get(textbook=tb, title=title)
        except Exception as e:
            print(e)
            continue
        ret_list.append(obj)

    return ret_list


def remove_empty_item(dict_data):
    if not isinstance(dict_data, dict):
        return False
    s_key = list(dict_data.keys())
    for k_s in s_key:
        if not dict_data[k_s]:
            del dict_data[k_s]
    return dict_data


if __name__ == '__main__':
    main_func("kp.xlsx")
