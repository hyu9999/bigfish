import datetime
import logging

from django.db.models import Avg, Sum, Value
from django.db.models.functions import Coalesce

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.schools.models import schools
from bigfish.apps.overall.models import KlassData, SchoolData
from bigfish.apps.visualbackend.backend.commons import compute_std_val, format_dict_param, get_current_term, \
    get_klass_list
from bigfish.utils.format_response import BFValidationError

logger = logging.getLogger('backend')


def write_to_school_data(term):
    qs_list = School.objects.filter(is_active=True, is_normal=True)
    write_basic_data(qs_list, term)
    write_complex_data(qs_list, term)


def write_basic_data(school_list, term):
    for obj in school_list:
        # basic info
        kwargs = get_basic_data(obj, term)
        # compute data
        compute_data = get_compute_data(obj, term)
        try:
            SchoolData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def write_complex_data(school_list, term):
    for obj in school_list:
        if not obj.areas:
            logger.error("该学校未配置区域！")
            continue
        # basic info
        kwargs = get_basic_data(obj, term)
        # compute data
        compute_data = get_compute_std_data(obj, term)
        try:
            SchoolData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def get_basic_data(school, term):
    """
    学校基础信息

    :param term:
    :param school: 学校
    :return:
    """
    ret_data = {
        "term": term, "school_id": school.id, "school_name": school.name, "short_name": school.short_name
    }
    try:
        ret_data.update({"district_code": school.areas.adcode, "district_name": school.areas.name})
    except Exception as e:
        logger.error(e)
        pass
    return ret_data


def get_compute_data(school, term):
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

    :param school: 学校
    :param term: 学期
    :return:
    """
    queryset = KlassData.objects.filter(school_id=school.id, term=term)
    basic_dict = queryset.aggregate(
        student_num_data=Coalesce(Sum('student_num'), Value(0)),
        teacher_num_data=Coalesce(Sum('teacher_num'), Value(0)),
        score_data=Coalesce(Avg('score'), Value(0)),
        right_rate_data=Coalesce(Avg('right_rate'), Value(0)),
        student_use_num_data=Coalesce(Sum('student_use_num'), Value(0)),
        student_use_duration_data=Coalesce(Sum('student_use_duration'), Value(0)),
        exercise_num_data=Coalesce(Avg('exercise_num'), Value(0)),
        interactive_num_data=Coalesce(Avg('interactive_num'), Value(0)),
        interactive_total_num_data=Coalesce(Sum('interactive_total_num'), Value(0)),
        teaching_progress_data=Coalesce(Avg('teaching_progress'), Value(0)),
        man_machine_num_data=Coalesce(Avg('man_machine_num'), Value(0)),
        activity_num_data=Coalesce(Sum('activity_num'), Value(0)),
        teacher_use_num_data=Coalesce(Sum('teacher_use_num'), Value(0)),
        teacher_use_duration_data=Coalesce(Sum('teacher_use_duration'), Value(0)),
        push_activity_num_data=Coalesce(Sum('push_activity_num'), Value(0)),
        task_num_data=Coalesce(Sum('task_num'), Value(0))
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
    print(type(basic_dict))
    basic_dict['center'] = "[{}]".format(school.position)
    ret_data = format_dict_param(basic_dict)
    return ret_data


def get_compute_std_data(school, term):
    """
    标准值，综合值

    :param obj: 学校
    :param term:
    :return:
    """
    ret_data = {}
    queryset = SchoolData.objects.filter(term=term, district_code=school.areas.adcode)
    try:
        data_obj = SchoolData.objects.get(term=term, school_id=school.id)
    except Exception as e:
        logger.error(e)
        return None

        # 使用时长标准值
    total_list = queryset.values_list("student_use_duration", flat=True)
    duration_std_val = compute_std_val(data_obj.student_use_duration, total_list)
    ret_data["duration_std_val"] = duration_std_val

    # 教学进度标准值
    total_list = queryset.values_list("teaching_progress", flat=True)
    teach_progress_std_val = compute_std_val(data_obj.teaching_progress, total_list)
    ret_data["teach_progress_std_val"] = teach_progress_std_val
    # 正确率标准值
    total_list = queryset.values_list("right_rate", flat=True)
    right_rate_std_val = compute_std_val(data_obj.right_rate, total_list)
    ret_data["right_rate_std_val"] = right_rate_std_val
    # 成绩标准值
    total_list = queryset.values_list("score", flat=True)
    score_std_val = compute_std_val(data_obj.score, total_list)
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
    use_num_std_val = compute_std_val(data_obj.student_use_num, total_list)
    ret_data["use_num_std_val"] = use_num_std_val
    # 使用次数标准值
    total_list = queryset.values_list("task_num", flat=True)
    use_times_std_val = compute_std_val(data_obj.task_num, total_list)
    ret_data["use_times_std_val"] = use_times_std_val
    # 交互次数标准值
    total_list = queryset.values_list("interactive_num", flat=True)
    interactive_num_std_val = compute_std_val(data_obj.interactive_num, total_list)
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
    if data_obj.student_num:
        use_num_ratio = float(data_obj.student_use_num) / data_obj.student_num
    else:
        use_num_ratio = 0
    use_num_ratio_std_val = compute_std_val(use_num_ratio, total_list)
    ret_data["use_num_ratio_std_val"] = use_num_ratio_std_val
    # 活动数量标准值
    total_list = queryset.values_list("activity_num", flat=True)
    activity_num_std_val = compute_std_val(data_obj.activity_num, total_list)
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
    write_to_school_data(t)
