import datetime
import logging

from django.db.models import Avg, Max, Min, Sum, Value
from django.db.models.functions import Coalesce

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.schools.models import PublishVersion
from bigfish.apps.areas.models import GDArea
from bigfish.apps.impactassessment.models import KlassWeekData, StudentWeekData
from bigfish.apps.visualbackend.backend.commons import get_current_school_week, format_dict_param, get_klass_list, \
    get_current_term, get_current_week

logger = logging.getLogger('backend')


def write_to_klass_week_data(week, klass_list):
    logger.info("write_to_klass_data start")
    for klass in klass_list:
        # basic info
        kwargs = get_basic_data(klass, week)
        logger.info("======================================{}".format(kwargs))
        # compute data
        compute_data = get_compute_data(klass, week)
        school_week = get_current_school_week(klass.school_id, week)
        if school_week:
            compute_data['school_week'] = school_week
        try:
            KlassWeekData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.error("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))

    logger.info("write_to_klass_data end")


def get_basic_data(obj, week):
    """
    班级基础信息

    :param obj: 班级
    :param week: 学校学周
    :return:
    """
    ret_data = {
        "term": week.term, "term_week": week, "klass_id": obj.id, "klass_name": obj.name,
        "grade_name": obj.grade, "school_id": obj.school.id, "school_name": obj.school.name,
        "short_name": obj.school.short_name}
    # publish
    try:
        publish_id = obj.publish_id
        city = PublishVersion.objects.get(id=publish_id)
    except Exception as e:
        logger.error(e)
    else:
        publish_name = city.name
        ret_data['publish_id'] = publish_id
        ret_data['publish_name'] = publish_name
    # area
    try:
        district_code = obj.school.areas.adcode
        district = GDArea.objects.get(adcode=district_code)
    except Exception as e:
        logger.error(e)
    else:
        district_name = district.name
        ret_data['district_code'] = district_code
        ret_data['district_name'] = district_name
        # city
        city_code = obj.school.areas.cityCode
        try:
            city = GDArea.objects.get(adcode=city_code)
        except Exception as e:
            logger.error(e)
            city_name = ""
        else:
            city_name = city.name
        ret_data['city_code'] = city_code
        ret_data['city_name'] = city_name
        # province
        province_code = obj.school.areas.provCode
        try:
            province = GDArea.objects.get(adcode=province_code)
        except Exception as e:
            logger.error(e)
            province_name = ""
        else:
            province_name = province.name
        ret_data['province_code'] = province_code
        ret_data['province_name'] = province_name
    return ret_data


def get_compute_data(klass, week):
    """
    right_rate      = 正确率
    max_score       = 最大成绩
    min_score       = 最小成绩
    avg_score       = 平均值
    use_duration    = 使用总时长
    interactive_num = 平均交互次数
    task_num        = 任务数

    :param klass:
    :param school_week:
    :return:
    """
    tmp_data = StudentWeekData.objects.filter(term_week=week, klass_id=klass.id).aggregate(
        right_rate_data=Coalesce(Avg('right_rate'), Value(0)),
        max_score_data=Coalesce(Max('max_score'), Value(0)),
        min_score_data=Coalesce(Min('min_score'), Value(0)),
        avg_score_data=Coalesce(Avg('avg_score'), Value(0)),
        use_duration_data=Coalesce(Sum('use_duration'), Value(0)),
        interactive_num_data=Coalesce(Avg('interactive_num'), Value(0)),
        task_num_data=Coalesce(Max('task_num'), Value(0)),
    )
    ret_data = format_dict_param(tmp_data)
    return ret_data


if __name__ == '__main__':
    kl = get_klass_list()
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    w = get_current_week(ct)
    write_to_klass_week_data(w, kl)
