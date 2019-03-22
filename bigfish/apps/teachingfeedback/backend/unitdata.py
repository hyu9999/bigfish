import datetime
import logging


from django.db.models import Avg, Sum, Q, F

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.schools.models import Unit, Klass
from bigfish.apps.reports.models import SaveDataInfo
from bigfish.apps.users.models import UserProfile
from bigfish.apps.teachingfeedback.models import UnitData, UnitTestData
from bigfish.apps.visualbackend.backend.commons import get_current_school_term, get_klass_list, get_current_term
from bigfish.apps.xiwo.models import SerialBindingRelation
from bigfish.utils.encrypt import convert_to_base_x
logger = logging.getLogger('backend')


def write_to_unit_data(term, klass_list):
    """
    right_rate = models.FloatField("平均正确率", blank=True, default=0.0)
    total_duration = models.FloatField("总时长", blank=True, default=0.0)
    :return:
    """
    for klass in klass_list:
        school_id = klass.school_id
        school_term = get_current_school_term(school_id, term)
        if school_term:
            query_duration = [school_term.start_date, school_term.finish_date]
        else:
            query_duration = [term.start_date, term.finish_date]
        query_all = SaveDataInfo.objects.filter(
            ~Q(textbook_id=0), ~Q(unit_id=0), ~Q(unit_title='Testing and review'), ~Q(lesson_title='单元测试'),
            klass_id=klass.id, add_time__date__range=query_duration, is_push=False
        ).values(
            'klass_id', 'unit_id'
        ).annotate(
            district_code=F('area_id'), district_name=F('area_name'),
            right_rate_data=Avg('right_rate'), total_duration=Sum('all_time')
        ).values('district_code', 'district_name', 'school_id', 'school_name', 'short_name', 'klass_id',
                 'klass_name', 'grade_name', 'publish_id', 'publish_name', 'unit_id', 'unit_title',
                 'right_rate_data', 'total_duration')

        for obj in query_all:
            kwargs = {"term": term, "klass_id": obj.get('klass_id'), "unit_id": obj.get('unit_id')}
            compute_data = {"right_rate": obj.get('right_rate_data'), "total_duration": obj.get('total_duration')}
            if not UnitData.objects.filter(**kwargs).exists():
                compute_data.update(obj)
                compute_data.pop("right_rate_data", None)
                klass_id = obj.get('klass_id')
                try:
                    teacher = UserProfile.objects.get(identity='老师', attend_class=klass_id)
                except Exception as e:
                    logger.error(e)
                else:
                    username = teacher.user.username
                    teacher_id = teacher.user_id
                    compute_data['username'] = username
                    compute_data['teacher_id'] = teacher_id
                try:
                    unit_num = Unit.objects.get(id=obj.get('unit_id')).order
                except Exception as e:
                    logger.error(e)
                else:
                    compute_data['unit_num'] = unit_num
            try:
                UnitData.objects.update_or_create(defaults=compute_data, **kwargs)
            except Exception as e:
                logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def write_to_unittest_data(term, klass_list):
    """

    :return:
    """
    for klass in klass_list:
        school_id = klass.school_id
        school_term = get_current_school_term(school_id, term)
        if school_term:
            query_duration = [school_term.start_date, school_term.finish_date]
        else:
            query_duration = [term.start_date, term.finish_date]
        #
        queryset = SaveDataInfo.objects.filter(
            ~Q(textbook_id=0), ~Q(unit_id=0), ~Q(unit_title='Testing and review'),
            lesson_title='单元测试', klass_id=klass.id,
            add_time__date__range=query_duration, is_push=False
        ).values(
            'unit_id'
        ).annotate(
            district_code=F('area_id'), district_name=F('area_name'), avg_score=Avg('score')
        ).values('district_code', 'district_name', 'school_id', 'school_name', 'short_name', 'klass_id',
                 'klass_name', 'grade_name', 'publish_id', 'publish_name', 'unit_id', 'unit_title', 'avg_score')

        for obj in queryset:
            kwargs = {"term": term, "klass_id": klass.id, "unit_id": obj.get('unit_id')}
            compute_data = {"score": obj.get('avg_score')}
            if not UnitTestData.objects.filter(**kwargs).exists():
                compute_data.update(obj)
                compute_data.pop("avg_score", None)
                klass_id = obj.get('klass_id')
                try:
                    teacher = UserProfile.objects.get(identity='老师', attend_class=klass_id)
                except Exception as e:
                    pass
                else:
                    username = teacher.user.username
                    teacher_id = teacher.user_id
                    compute_data['username'] = username
                    compute_data['teacher_id'] = teacher_id
                try:
                    unit_num = Unit.objects.get(id=obj.get('unit_id')).order
                except Exception as e:
                    pass
                else:
                    compute_data['unit_num'] = unit_num
            try:
                UnitTestData.objects.update_or_create(defaults=compute_data, **kwargs)
            except Exception as e:
                logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def check_bind(serial_num, device_code):
    bind_status, is_invalid = True, True
    serial_num = int(serial_num, base=32)
    print(serial_num)
    user = None
    try:
        sbr = SerialBindingRelation.objects.get(serial_num__serial_num=serial_num, device_code=device_code)
    except Exception as e:
        print(e)
        bind_status = False
    else:
        user = sbr.user
        current_time = datetime.datetime.now()
        if sbr.invalid_time > current_time:
            is_invalid = False
    return bind_status, is_invalid, user


if __name__ == '__main__':
    # ct = datetime.datetime.now()
    # t = get_current_term(ct)
    # k = get_klass_list()
    # write_to_unit_data(t, k)
    # write_to_unittest_data(t, k)
    encrypted_serial = convert_to_base_x(180955946, 32)
    print(encrypted_serial)
    sn, dc = encrypted_serial, 'BFEBFBFF000906E94c44535937313136303032323235202020202020'
    aa = check_bind(sn, dc)
    print(aa)
