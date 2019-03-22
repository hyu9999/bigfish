# coding=utf8
import logging

import xlrd
from django.db import transaction

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.textbooks.models import Unit, Textbook
from bigfish.apps.knowledgepoint.models import KnowledgePoint

logger = logging.getLogger('backend')


def main_func(file_path):
    """
    知识点整表导入

    :param file_path:
    :return:
    """
    # 打开文件
    workbook = xlrd.open_workbook(file_path)
    # # 根据sheet索引或者名称获取sheet内容
    sheets_list = workbook.sheet_names()
    sheet_num = len(sheets_list)

    for j in range(sheet_num):
        last_obj = None
        sheet2 = workbook.sheet_by_index(j)  # sheet索引从0开始
        with transaction.atomic():
            for i in range(1, sheet2.nrows):
                data_list = sheet2.row_values(i)
                name, root, level, order, has_children, curriculum_standard, unit, desc = data_list
                if unit:
                    unit_list = get_unit_list(unit)
                else:
                    unit_list = []
                print(name, root, level, order, has_children, curriculum_standard, unit, desc)
                if not has_children or str(has_children).replace(" ", "") == "":
                    has_children = False
                else:
                    has_children = True
                if not curriculum_standard or str(curriculum_standard).replace(" ", "") == "":
                    curriculum_standard = False
                else:
                    curriculum_standard = True
                defaults = {"has_children": has_children, "curriculum_standard": curriculum_standard, "desc": desc,
                            "root": root}
                defaults = remove_empty_item(defaults)
                kwargs = {"name": name, "level": level, "order": order}
                if i == 1:
                    if level == 1:
                        last_obj, flag = KnowledgePoint.objects.update_or_create(defaults=defaults, **kwargs)
                        pass
                    else:
                        logger.error("第一条必须是一级!")
                        break
                else:
                    last_data_list = sheet2.row_values(i - 1)
                    last_level = last_data_list[2]

                    # 下一级
                    if level > last_level:
                        kwargs['parent_code'] = last_obj.coding

                    # 同级
                    elif level == last_level:
                        if level != 1:
                            kwargs['parent_code'] = last_obj.parent_code
                    # 其他级别
                    else:
                        if level != 1:
                            brother_knowledge = get_brother_knowledge(last_obj, level)
                            if brother_knowledge:
                                kwargs['parent_code'] = brother_knowledge.parent_code
                            else:
                                logger.error("获取父节点失败！")
                                break

                    last_obj, flag = KnowledgePoint.objects.update_or_create(defaults=defaults, **kwargs)
                    if not flag:
                        last_obj.unit.remove()
                    for unit_obj in unit_list:
                        last_obj.unit.add(unit_obj)


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
    main_func("all_kp.xlsx")
    # pool = multiprocessing.Pool(processes=3)
    # for i in range(0, 3):
    #     msg = "hello %d" % (i)
    #     pool.apply_async(main_func, ("a.xlsx",))
    # pool.close()
    # pool.join()  # behind close() or terminate()
    # print("Sub-process(es) done.")
