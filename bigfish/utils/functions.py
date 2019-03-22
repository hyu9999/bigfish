# encoding: utf-8

"""
@author: h3l
@contact: xidianlz@gmail.com
@file: functions.py
@time: 2017/6/22 15:46
"""
from collections import OrderedDict
from datetime import datetime, timedelta

import pypinyin
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import Field
from pypinyin import pinyin
from rest_framework.exceptions import ValidationError

from bigfish.apps.bfwechat.models import WxUser
from bigfish.apps.schools.models import Klass
from bigfish.apps.users.models import UserKlassRelationship, BigfishUser
from bigfish.base.response import BFValidationError, BFPermissionDenied


def generate_fields(model, add=None, remove=None):
    if add is None:
        add = []
    if remove is None:
        remove = []

    remove.append("id")
    result = []
    for field in model._meta.get_fields():
        if isinstance(field, Field):
            result.append(field.name)
    for item in add:
        result.append(item)
    for item in remove:
        try:
            result.remove(item)
        except ValueError:
            pass

    return tuple(result)


def generate_file_name(suffix):
    now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
    return "{}.{}".format(now, suffix)


def generate_file_name_windows(suffix):
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
    return "{}.{}".format(now, suffix)


def remove_key(data, keys=None):
    if keys is None:
        keys = []
    for key in keys:
        data.pop(key, None)
    return data


def get_error_info(serializer, name_mapping):
    error = serializer.errors
    translated_error = OrderedDict()
    for error_field in error:
        try:
            translated_error[name_mapping[error_field]] = error[error_field]
        except:
            translated_error['record_error'] = error[error_field]
    return translated_error


def generate_username(identity, username_full, school_code):
    username = ""
    if identity == '学生':
        username += "s"
    elif identity == '老师':
        username += "t"
    else:
        return None
    username += str(school_code)[-3:]
    pinyin_list = ''.join([x[0] for x in pinyin(username_full, pypinyin.FIRST_LETTER)])
    username += pinyin_list
    user_list = User.objects.filter(username__startswith=username).order_by('-id')
    try:
        suffix = str(int(user_list.first().username[len(username):]) + 1)
    except Exception as e:
        suffix = '1'
    username += suffix
    return username


def generate_num_username(identity, school_code):
    username = ""
    # 1.角色 1：老师         2：学生
    if identity == 2:
        username += "1"
    elif identity == 1:
        username += "2"
    else:
        return None
    # 2.学校码
    username += str(school_code)[-3:]
    # 3.用户自增序号
    user_list = BigfishUser.objects.filter(username__startswith=username).order_by('-id')
    try:
        max_id = int(user_list.first().username[len(username):]) + 1
        if max_id >= 1000:
            suffix = str(max_id)
        else:
            suffix = str(max_id).zfill(4)
    except Exception as e:
        suffix = '0001'
    username += suffix
    return username


def generate_num_wx_user(username):
    try:
        default_klass = UserKlassRelationship.objects.filter(user__username=username, is_default=True).first().klass
        default_cid = default_klass.id
    except Exception as e:
        raise ValidationError("获取用户信息失败")
    try:
        klass = Klass.objects.get(id=int(default_cid))
        school_code = klass.school.coding
    except Exception as e:
        raise ValidationError("获取学校信息失败")
    username = ""
    # 1.角色
    username += "1"
    # 2.学校码
    username += str(school_code)[-3:]
    # 3.用户自增序号
    user_list = WxUser.objects.filter(username__startswith=username).order_by('-id')
    try:
        max_id = int(user_list.first().username[len(username):]) + 1
        if max_id >= 1000:
            suffix = str(max_id)
        else:
            suffix = str(max_id).zfill(4)
    except Exception as e:
        suffix = '0001'
    username += suffix
    return username


def fmt_query_params(dict_data):
    if not isinstance(dict_data, dict):
        return None
    ret_dict = {}
    for k, v in dict_data.items():
        if v:
            if isinstance(v, str):
                val = str(v).strip()
            else:
                val = v
            ret_dict[k] = val
    return ret_dict


def get_range_time(date_val, from_val=1, to_val=1, from_monday=True):
    if from_monday:
        days_count = timedelta(days=date_val.isoweekday())
    else:
        days_count = 0
    day_from = date_val - days_count + timedelta(days=from_val)
    day_to = date_val - days_count + timedelta(days=to_val)
    return day_from, day_to


def get_field_name(model, *verbose_name_list):
    result = []
    all_field = model._meta.get_fields()
    for item in verbose_name_list:
        try:
            name = [x.name for x in all_field if x.verbose_name == item][0]
        except Exception as e:
            continue
        else:
            result.append(name)
    return result


def format_admin_list(model, add=None, remove=None):
    if add is None:
        add = []
    if remove is None:
        remove = []

    result = []
    for field in model._meta.get_fields():
        if isinstance(field, Field):
            if not isinstance(field, models.ManyToManyField):
                result.append(field.name)
    for item in add:
        result.append(item)
    for item in remove:
        try:
            result.remove(item)
        except ValueError:
            pass

    return tuple(result)


def format_admin_search_fields(model, add=None, remove=None):
    if add is None:
        add = []
    if remove is None:
        remove = []

    result = []
    for field in model._meta.get_fields():
        if isinstance(field, Field):
            if isinstance(field, models.ManyToManyField) or isinstance(field, models.ForeignKey) \
                    or isinstance(field, models.OneToOneField):
                continue
            result.append(field.name)
    for item in add:
        result.append(item)
    for item in remove:
        try:
            result.remove(item)
        except ValueError:
            pass

    return tuple(result)


def format_admin_editable(model, add=None, remove=None):
    if add is None:
        add = []
    if remove is None:
        remove = []

    result = []
    for field in model._meta.get_fields():
        if isinstance(field, Field):
            if isinstance(field, models.BooleanField):
                result.append(field.name)
    for item in add:
        result.append(item)
    for item in remove:
        try:
            result.remove(item)
        except ValueError:
            pass

    return tuple(result)


def get_key_by_value(model_choice, val):
    ret_data = None
    data = dict(model_choice)
    data_list = [x for x, y in data.items() if y == val]
    if len(data_list) != 0:
        ret_data = data_list[0]
    return ret_data


def check_env_wx(view):
    """
    检查微信环境

    :param view:
    :return:
    """

    def decorator(request, *args, **kwargs):
        # 判断对象中是否包含属性
        if hasattr(request, "META"):
            req = request
        elif hasattr(request, "request"):
            req = request.request
        else:
            raise BFValidationError("未知环境！")
        try:
            user_agent = str(req.META.get("HTTP_USER_AGENT")).lower()
        except Exception as e:
            raise BFValidationError("未知环境！【{}】".format(e))
        if "micromessenger" in user_agent:
            return view(request, *args, **kwargs)
        raise BFPermissionDenied("请从微信端访问")

    return decorator


def media_fields(model):
    result = []
    for field in model._meta.get_fields():
        if isinstance(field, Field):
            if isinstance(field, models.ImageField) or isinstance(field, models.FileField):
                result.append(field.name)
    return tuple(result)
