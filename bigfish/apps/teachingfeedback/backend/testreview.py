import datetime
import logging

from django.db.models import Avg, Sum, F, Value
from django.db.models.functions import Coalesce

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.reports.models import SaveDataInfo
from bigfish.apps.teachingfeedback.models import TestReview
from bigfish.apps.visualbackend.backend.commons import format_dict_param, get_current_school_term, get_current_term, \
    get_klass_list

logger = logging.getLogger('backend')


def write_to_test_review_data(term, klass_list):
    """
    写入TestReview表

    :return:
    """
    for klass in klass_list:
        school_id = klass.school_id
        school_term = get_current_school_term(school_id, term)
        if school_term:
            query_duration = [school_term.start_date, school_term.finish_date]
        else:
            query_duration = [term.start_date, term.finish_date]
        # 单元检测
        kwargs_base = {"add_time__date__range": query_duration, "klass_id": klass.id, "is_push": False}
        lesson_title_list = ['单元检测', '期中模拟', '单元复习', '综合复习']
        for item in lesson_title_list:
            tmp_data = SaveDataInfo.objects.filter(lesson_title=item, **kwargs_base).values('lesson_title').annotate(
                total_duration=Coalesce(Sum('all_time'), Value(0)),
                right_rate_data=Coalesce(Avg('right_rate'), Value(0)),
                score_data=Coalesce(Avg('score'), Value(0)),
                district_code=F('area_id'), district_name=F('area_name')
            ).values('district_code', 'district_name', 'school_id', 'school_name', 'short_name', 'klass_id',
                     'klass_name', 'grade_name', 'total_duration', 'right_rate_data', 'score_data')
            if tmp_data.exists():
                sdi = format_dict_param(dict(tmp_data[0]))
                kwargs = {"term": term, "klass_id": klass.id, 'lesson_title': item}
                TestReview.objects.update_or_create(defaults=sdi, **kwargs)


if __name__ == '__main__':
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    k = get_klass_list()
    write_to_test_review_data(t, k)
