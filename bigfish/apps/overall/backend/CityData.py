import datetime
import logging

from django.db.models import Avg, Sum

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.areas.models import GDArea
from bigfish.apps.overall.models import DistrictData, CityData
from bigfish.apps.visualbackend.backend.commons import compute_std_val, format_dict_param, get_current_term

logger = logging.getLogger('backend')


def write_to_city_data(term):
    qs_list = GDArea.objects.filter(is_active=True, level='city')
    write_basic_data(qs_list, term)
    write_complex_data(term)


def write_basic_data(city_list, term):
    for city in city_list:
        sd_qs = DistrictData.objects.filter(term=term, city_code=city.adcode).exists()
        if not sd_qs:
            logger.info("[{}]{} :该市下无数据".format(city.adcode, city.name))
            continue
        # basic info
        kwargs = get_basic_data(city, term)
        # compute data
        compute_data = get_compute_data(city, term)

        try:
            CityData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def write_complex_data(term):
    qs_list = CityData.objects.filter(term=term)
    for city_data in qs_list:
        # basic info
        kwargs = {"id": city_data.id}
        # compute data
        compute_data = get_compute_std_data(city_data, term)
        try:
            CityData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def get_basic_data(city, term):
    """
    地区基础信息

    :param term:
    :param city: 城市
    :return:
    """
    ret_data = {
        "term": term, "province_code": city.provCode, "city_code": city.adcode, "city_name": city.name
    }
    try:
        prov = GDArea.objects.get(adcode=city.provCode)
    except Exception as e:
        logger.exception(e)
    else:
        ret_data["province_name"] = prov.name
    return ret_data


def get_compute_data(city, term):
    """
    某个xx学生的成绩平均值
    某个xx各个学生的正确率平均值
    某个xx学生的数量
    某个xx使用pad的学生的数量
    某个xx教师的实际数量
    某个xx使用pad的教师的数量
    某个xx学生的练习题数平均值
    某个xx学生的交互次数平均值
    某个xx学生的交互次数之和
    某个xx教师的教学进度平均值
    某个xx学生的人机对话量平均值
    使用次数
    活动数量
    使用次数上限

    :param obj: 城市
    :param term: 学期
    :return:
    """

    basic_dict = DistrictData.objects.filter(city_code=city.adcode, term=term).aggregate(
        student_num_data=Sum('student_num'), teacher_num_data=Sum('teacher_num'),
        score_data=Avg('score'),
        right_rate_data=Avg('right_rate'),
        student_use_num_data=Sum('student_use_num'), student_use_duration_data=Sum('student_use_duration'),
        exercise_num_data=Avg('exercise_num'),
        interactive_num_data=Avg('interactive_num'),
        interactive_total_num_data=Sum('interactive_total_num'),
        teaching_progress_data=Avg('teaching_progress'),
        man_machine_num_data=Avg('man_machine_num'),
        activity_num_data=Sum('activity_num'),
        teacher_use_num_data=Sum('teacher_use_num'), teacher_use_duration_data=Sum('teacher_use_duration'),
        push_activity_num_data=Sum('push_activity_num'),
        task_num_data=Sum('task_num')
    )
    try:
        saud = round(basic_dict.get('student_use_duration_data') * 1.0 / basic_dict.get('student_use_num_data'), 2)
    except Exception as e:
        saud = 0
    basic_dict['student_avg_use_duration'] = saud
    try:
        taud = round(basic_dict.get('teacher_use_duration_data') * 1.0 / basic_dict.get('teacher_use_num_data'), 2)
    except Exception as e:
        taud = 0
    basic_dict['teacher_avg_use_duration'] = taud
    basic_dict['center'] = city.center
    ret_data = format_dict_param(basic_dict)
    return ret_data


def get_compute_std_data(city_data, term):
    """
    标准值，综合值

    :param city_data: 城市
    :param term:
    :return:
    """
    ret_data = {}
    queryset = CityData.objects.filter(term=term, province_code=city_data.province_code)

    # 使用时长标准值
    total_list = queryset.values_list("student_use_duration", flat=True)
    duration_std_val = compute_std_val(city_data.student_use_duration, total_list)
    ret_data["duration_std_val"] = duration_std_val

    # 教学进度标准值
    total_list = queryset.values_list("teaching_progress", flat=True)
    teach_progress_std_val = compute_std_val(city_data.teaching_progress, total_list)
    ret_data["teach_progress_std_val"] = teach_progress_std_val
    # 正确率标准值
    total_list = queryset.values_list("right_rate", flat=True)
    right_rate_std_val = compute_std_val(city_data.right_rate, total_list)
    ret_data["right_rate_std_val"] = right_rate_std_val
    # 成绩标准值
    total_list = queryset.values_list("score", flat=True)
    score_std_val = compute_std_val(city_data.score, total_list)
    ret_data["score_std_val"] = score_std_val
    """
    1.教学进度(0.2)
    2.平均正确率(0.35)
    3.阶段成绩(0.45)
    综合值 = 标准值1*权重1 + 标准值2*权重2 + 标准值3*权重3
    """
    composite = teach_progress_std_val * 0.2 + right_rate_std_val * 0.35 + score_std_val * 0.45
    ret_data["composite"] = composite

    # 使用人数标准值
    total_list = queryset.values_list("student_use_num", flat=True)
    use_num_std_val = compute_std_val(city_data.student_use_num, total_list)
    ret_data["use_num_std_val"] = use_num_std_val
    # 使用次数标准值
    total_list = queryset.values_list("task_num", flat=True)
    use_times_std_val = compute_std_val(city_data.task_num, total_list)
    ret_data["use_times_std_val"] = use_times_std_val
    # 交互次数标准值
    total_list = queryset.values_list("interactive_num", flat=True)
    interactive_num_std_val = compute_std_val(city_data.interactive_num, total_list)
    ret_data["interactive_num_std_val"] = interactive_num_std_val
    """
    1.使用人数(0.2)
    2.使用次数(0.3)
    3.交互次数(0.5)
    综合值 = 标准值1*权重1 + 标准值2*权重2 + 标准值3*权重3
    """
    as_composite = use_num_std_val * 0.2 + use_times_std_val * 0.3 + interactive_num_std_val * 0.5
    ret_data["as_composite"] = as_composite

    # 使用人数比例标准值
    total_list = [0 if y == 0 else float(x) / y for (x, y) in queryset.values_list("student_num", "student_use_num")]
    if city_data.student_num:
        use_num_ratio = float(city_data.student_use_num) / city_data.student_num
    else:
        use_num_ratio = 0
    use_num_ratio_std_val = compute_std_val(use_num_ratio, total_list)
    ret_data["use_num_ratio_std_val"] = use_num_ratio_std_val
    # 活动数量标准值
    total_list = queryset.values_list("activity_num", flat=True)
    activity_num_std_val = compute_std_val(city_data.activity_num, total_list)
    ret_data["activity_num_std_val"] = activity_num_std_val
    """
    1.使用人数比例(0.3) = 使用人数/总人数
    2.交互次数(0.3)
    3.活动数量(0.4)
    使用情况综合值 = 标准值1*权重1 + 标准值2*权重2 + 标准值3*权重3
    """
    usage_composite = use_num_std_val * 0.3 + use_times_std_val * 0.3 + interactive_num_std_val * 0.4
    ret_data["usage_composite"] = usage_composite
    return ret_data


if __name__ == '__main__':
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    write_to_city_data(t)
