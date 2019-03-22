import logging

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.schools.models import Klass
from bigfish.apps.research.models import TermSchedule, SchoolWeek, TermWeek, Term
import numpy as np

logger = logging.getLogger('django')


def get_current_term(current_time):
    try:
        date = current_time.date()
        term_obj = Term.objects.get(start_date__lte=date, finish_date__gte=date)
    except Exception as e:
        print("获取学期信息失败！[{}]".format(e))
        return None
    # for test
    # term_obj = Term.objects.get(order=4)
    return term_obj


def get_current_week(current_time):
    try:
        date = current_time.date()
        week = TermWeek.objects.get(start_date__lte=date, finish_date__gte=date)
    except Exception as e:
        print("获取学期信息失败！[{}]".format(e))
        return None
    # for test
    # term_obj = Term.objects.get(order=4)
    return week


def get_current_school_term(school_id, term):
    if not school_id:
        return None
    try:
        term_obj = TermSchedule.objects.get(school_id=school_id, term=term)
    except Exception as e:
        print("获取学校学期信息失败！[{}]".format(e))
        return None
    return term_obj


def get_current_school_week(school_id, week):
    if not school_id:
        return None
    try:
        term_obj = SchoolWeek.objects.get(school_id=school_id, term_week=week)
    except Exception as e:
        print("获取学校学周信息失败！[{}]".format(e))
        return None
    return term_obj


def get_school_week(term):
    obj = SchoolWeek.objects.filter(term=term).order_by('order')
    return obj


def get_klass_list():
    klass_list = Klass.objects.filter(is_active=True, school__is_normal=True, school__is_active=True)
    return klass_list


def get_user_basic_data(user_profile):
    username = user_profile.user.username
    ret_dict = {"username": username}
    klass = user_profile.attend_class.all().first()
    klass_id = klass.id
    ret_dict['klass_id'] = klass_id
    klass_name = klass.name
    ret_dict['klass_name'] = klass_name
    grade_name = klass.grade
    ret_dict['grade_name'] = grade_name
    school_id = klass.school.id
    ret_dict['school_id'] = school_id
    school_name = klass.school.name
    ret_dict['school_name'] = school_name
    short_name = klass.school.short_name
    ret_dict['short_name'] = short_name
    try:
        district_code = klass.school.areas.adcode
        district = klass.school.areas.name
        province = klass.school.areas.provCode
        city = klass.school.areas.cityCode
    except Exception as e:
        logger.error("未配置区域")
        district_code = 0
        district = ""
        province = 0
        city = 0
    ret_dict['district_code'] = district_code
    ret_dict['district'] = district
    ret_dict['province'] = province
    ret_dict['city'] = city
    logger.debug(ret_dict)
    return ret_dict


def compute_std_val(single_avg, total_list):
    """
    标准值计算

    公式：（单个值 - 所有值的平均值）/ 标准差

    :param single_avg:
    :param total_list:
    :return:
    """
    total_avg = np.mean(total_list)
    std = np.std(total_list)
    if std:
        std_val = (single_avg - total_avg) / std
    else:
        std_val = 0
    return std_val


def format_dict_param(src_data):
    ret_data = {}
    for key, val in src_data.items():
        if key.endswith("_data"):
            new_key = key[:-5]
        else:
            new_key = key
        if val is None:
            ret_data[new_key] = 0
        else:
            ret_data[new_key] = val
    return ret_data


def remove_empty_item(dict_data):
    if not isinstance(dict_data, dict):
        return False
    s_key = list(dict_data.keys())
    for k_s in s_key:
        if not dict_data[k_s]:
            del dict_data[k_s]
    return dict_data


if __name__ == '__main__':
    # tm = get_current_term()
    # print(tm)
    # data = {"a": "", "b": None, "c": [], "d": 0, "e": "ee"}
    # dd = remove_empty_item(data)
    # print(dd)
    get_current_school_week(1)
