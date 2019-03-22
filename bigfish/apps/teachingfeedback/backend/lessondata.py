import datetime
import logging

from django.db.models import Avg, Sum, Q, F

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.schools.models import Unit
from bigfish.apps.reports.models import SaveDataInfo
from bigfish.apps.users.models import UserProfile
from bigfish.apps.teachingfeedback.models import LessonData
from bigfish.apps.visualbackend.backend.commons import get_current_school_term, get_current_term, get_klass_list

logger = logging.getLogger('backend')


def write_to_lesson_data(term, klass_list):
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
            ~Q(textbook_id=0), ~Q(unit_id=0), ~Q(lesson_id=0), ~Q(unit_title='Testing and review'),
            ~Q(lesson_title='单元测试'), klass_id=klass.id, add_time__date__range=query_duration, is_push=False
        ).values(
            'klass_id', 'lesson_id'
        ).annotate(
            district_code=F('area_id'), district_name=F('area_name'),
            right_rate_data=Avg('right_rate'), total_duration=Sum('all_time')
        ).values('district_code', 'district_name', 'school_id', 'school_name', 'short_name', 'klass_id',
                 'klass_name',
                 'grade_name', 'publish_id', 'publish_name', 'unit_id', 'unit_title', 'lesson_id',
                 'lesson_title', 'lesson_order', 'right_rate_data', 'total_duration')

        for obj in query_all:
            kwargs = {"term": term, "klass_id": obj.get('klass_id'), "lesson_id": obj.get('lesson_id')}
            compute_data = {"right_rate": obj.get('right_rate_data'), "total_duration": obj.get('total_duration')}
            if not LessonData.objects.filter(**kwargs).exists():
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
                LessonData.objects.update_or_create(defaults=compute_data, **kwargs)
            except Exception as e:
                logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


if __name__ == '__main__':
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    k = get_klass_list()
    write_to_lesson_data(t, k)
