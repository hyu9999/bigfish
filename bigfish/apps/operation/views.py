import logging

from bigfish.apps.areas.models import Area
from bigfish.apps.operation.models import OperationRecord, ActClick
from bigfish.apps.operation.serializers import OperationRecordSerializer, ActClickSerializer
from bigfish.apps.users.models import UserKlassRelationship
from bigfish.base import viewsets
from bigfish.base.response import BFValidationError

logger = logging.getLogger("django")


class OperationRecordViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a OperationRecord instance.
    list:
        Return all OperationRecord, ordered by most recently joined.
    create:
        Create a new OperationRecord.
    delete:
        Remove an existing OperationRecord.
    partial_update:
        Update one or more fields on an existing OperationRecord.
    update:
        Update a OperationRecord.
    """
    queryset = OperationRecord.objects.all()
    serializer_class = OperationRecordSerializer


def create_or_update_operate(user, lesson, dict_param, operate_data):
    """
    更新创建操作记录公共方法

    :param user:
    :param lesson:
    :param dict_param:
        {
        "scene":1,          # 场景
        "is_finish":true,
        "duration":1
        "finish_num":1,
        "unfinished_num":1,
        "has_score":True,
        "avg_score":1,
        "start_time":"2019-01-11 00:00:00",
        "finish_time":"2019-01-11 00:00:00",
        }
    :param kwargs:\n
        {
        "classroom_id":1,   # 课堂必填
        "operate_type":1,   # 操作类型
        "operation_id":1,   # 操作行为ID
        "operate_id":1      # 操作内容ID(活动ID,课堂ID等)
        }
    :return:
    """
    defaults = {"user_id": user.id, "identity": user.identity}
    if all([isinstance(dict_param, dict), isinstance(operate_data, dict)]):
        pass
    else:
        raise BFValidationError("传入参数类型错误")
    defaults.update(dict_param)
    user_info = get_user_data(user)
    defaults.update(user_info)
    textbook_info = get_textbook_data(lesson)
    defaults.update(textbook_info)
    operation_record, created = OperationRecord.objects.update_or_create(defaults=defaults, **operate_data)
    return operation_record


def get_user_data(user):
    """用户数据 (AbsPersonalRpt)"""
    try:
        user_klass = UserKlassRelationship.objects.get(user=user, is_default=True)
    except:
        raise BFValidationError('用户没有默认班级')
    try:
        city = Area.objects.get(coding=user_klass.klass.school.areas.city_code)
        prov = Area.objects.get(coding=user_klass.klass.school.areas.prov_code)
    except:
        raise BFValidationError('班级配置的地区有误')
    user_data = {
        'username': user.username,
        'realname': user.realname,
        'nickname': user.nickname,
        'klass_id': user_klass.klass.id,
        'klass_name': user_klass.klass.title,
        'grade_name': user_klass.klass.grade,
        'school_id': user_klass.klass.school.id,
        'school_name': user_klass.klass.school.title,
        'short_name': user_klass.klass.school.short_name,
        'area_id': user_klass.klass.school.areas.coding,
        'area_name': user_klass.klass.school.areas.name,
        'city_name': city.name,
        'city_code': user_klass.klass.school.areas.city_code,
        'province_name': prov.name,
        'province_code': user_klass.klass.school.areas.prov_code,
    }
    return user_data


def get_textbook_data(lesson):
    """教材数据"""
    if lesson:
        publish_data = {
            # 'publish_id': lesson.unit.textbook.publish.id,
            'publish_name': lesson.unit.textbook.publish.title,
            'textbook_id': lesson.unit.textbook.id,
            'textbook_name': lesson.unit.textbook.title,
            'term_num': lesson.unit.textbook.term,
            'unit_id': lesson.unit.id,
            'unit_name': lesson.unit.title,
            'lesson_id': lesson.id,
            'lesson_name': lesson.title,
            'lesson_order': lesson.order
        }
    else:
        publish_data = {}
    return publish_data


class ActClickViewSet(viewsets.ModelViewSet):
    """"""
    queryset = ActClick.objects.all()
    serializer_class = ActClickSerializer
