import logging
from collections import OrderedDict

from ajax_select.registry import get_model
from rest_framework.exceptions import ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict

logger = logging.getLogger('django')


def get_queryset_freedom(app_name, model_name, query_condition, field_name_list):
    exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
    try:
        exec(exec_str)
    except Exception as e:
        logger.debug(e)
        raise ValidationError("引入模块失败")
    try:
        if query_condition:
            val_list = eval(
                '{}.objects.filter(**{}).values_list(*{})'.format(model_name, query_condition, field_name_list))
        else:
            val_list = eval('{}.objects.all().values_list(*{})'.format(model_name, field_name_list))
    except Exception as e:
        logger.debug(e)
        raise ValidationError("获取查询结果集失败")
    return val_list


def import_model_freedom(app_name, model_name):
    exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
    try:
        exec(exec_str)
    except Exception as e:
        logger.debug(e)
        raise ValidationError("引入模块失败")


def import_serializer_freedom(app_name, model_name):
    exec_str = 'from bigfish.apps.{}.serializers import {}Serializer'.format(app_name, model_name)
    try:
        exec(exec_str)
    except Exception as e:
        logger.debug(e)
        raise ValidationError("引入模块失败")


def get_model_obj_freedom(app_name, model_name):
    import_model_freedom(app_name, model_name)
    model_obj = get_model(app_name, model_name)
    return model_obj


def get_model_fields_freedom(app_name, model_name, query_field_list=[], remove_field_list=[]):
    field_dic = OrderedDict()
    model_obj = get_model_obj_freedom(app_name, model_name)
    if not query_field_list:
        for field in model_obj._meta.fields:
            if field.name in remove_field_list:
                continue
            field_dic[field.name] = field.verbose_name
            logger.debug('字段类型:', type(field).__name__)  # 返回的是‘charfield’,'textfield',等这些类型
    else:
        for index, field_name in enumerate(query_field_list):
            try:
                exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
                try:
                    exec(exec_str)
                except Exception as e:
                    logger.debug(e)
                    raise ValidationError("引入模块失败")
                exec("from django_filters.utils import get_model_field")
                model_field = eval('get_model_field({}, field_name).verbose_name'.format(model_name))
            except Exception as e:
                logger.debug(e)
                model_field = field_name
            field_dic[field_name] = str(model_field)
    return field_dic
