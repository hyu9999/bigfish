import datetime
import logging

import numpy as np
import stats as sts
from django.db.models import Avg, Count, Sum, Value
from django.db.models.functions import Coalesce

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.utils.format_response import BFValidationError
from bigfish.apps.overall.models import KlassData
from bigfish.apps.users.models import UserProfile
from bigfish.apps.visualbackend.models import TeacherData, StudentData, StageScore
from bigfish.apps.visualbackend.backend.commons import compute_std_val, format_dict_param, get_klass_list, \
    get_current_term

logger = logging.getLogger('backend')


def write_to_klass_data(term, klass_list):
    logger.info("write_to_klass_data start")
    write_basic_data(klass_list, term)
    write_complex_data(klass_list, term)
    logger.info("write_to_klass_data end")


def write_basic_data(klass_list, term):
    for obj in klass_list:
        # basic info
        kwargs = get_basic_data(obj, term)
        logger.info(kwargs)
        # compute data
        compute_data = get_compute_data(obj, term)
        try:
            KlassData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def write_complex_data(klass_list, term):
    for obj in klass_list:
        # basic info
        kwargs = get_basic_data(obj, term)
        # compute data
        compute_data = get_klass_compute_std_data(obj, term)
        # stage score
        stage_score_data = get_klass_stage_score(obj, term)
        compute_data.update(stage_score_data)
        try:
            KlassData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def get_basic_data(klass, term):
    """
    班级基础信息

    :param klass: 班级
    :param term: 学期
    :return:
    """
    ret_data = {
        "term": term, "klass_id": klass.id, "klass_name": klass.name, "grade_name": klass.grade,
        "school_id": klass.school.id, "school_name": klass.school.name, "short_name": klass.school.short_name
    }
    try:
        ret_data.update({"district_code": klass.school.areas.adcode, "district_name": klass.school.areas.name})
    except Exception as e:
        logger.error(e)
    return ret_data


def get_compute_data(klass, term):
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

    :param klass:
    :param term:
    :return:
    """

    student_num = UserProfile.objects.filter(attend_class=klass, identity='学生').aggregate(data=Count('user_id')).get(
        'data')
    teacher_num = UserProfile.objects.filter(attend_class=klass, identity='老师').aggregate(data=Count('user_id')).get(
        'data')
    tmp_data = {"student_num": student_num, "teacher_num": teacher_num}
    stu_data_dict = StudentData.objects.filter(term=term, klass_id=klass.id, in_use=True).aggregate(
        score_data=Coalesce(Avg('score'), Value(0)),
        right_rate_data=Coalesce(Avg('right_rate'), Value(0)),
        student_use_num_data=Count('username'),
        student_use_duration_data=Coalesce(Sum('use_duration'), Value(0)),
        student_avg_use_duration_data=Sum('use_duration') / Count('username'),
        exercise_num_data=Coalesce(Avg('exercise_num'), Value(0)),
        interactive_num_data=Coalesce(Avg('interactive_num'), Value(0)),
        interactive_total_num_data=Coalesce(Sum('interactive_num'), Value(0)),
        man_machine_num_data=Coalesce(Avg('man_machine_num'), Value(0)),
        activity_num_data=Coalesce(Sum('activity_num'), Value(0)),
    )
    tmp_data.update(stu_data_dict)
    teacher_data_dict = TeacherData.objects.filter(term=term, klass_id=klass.id, in_use=True).aggregate(
        teacher_use_num_data=Count('username'),
        teacher_use_duration_data=Coalesce(Sum('use_duration'), Value(0)),
        teacher_avg_use_duration_data=Sum('use_duration') / Count('username'),
        push_activity_num_data=Coalesce(Sum('push_activity_num'), Value(0)),
        teaching_progress_data=Coalesce(Avg('teaching_progress'), Value(0)),
        task_num_data=Coalesce(Sum('task_num'), Value(0))
    )
    tmp_data.update(teacher_data_dict)
    ret_data = format_dict_param(tmp_data)
    return ret_data


def get_klass_compute_std_data(klass, term):
    """
    标准值，综合值

    :param klass:
    :param term:
    :return:
    """
    ret_data = {}
    queryset = KlassData.objects.filter(term=term, school_id=klass.school.id)
    try:
        klass_data_obj = KlassData.objects.get(term=term, klass_id=klass.id)
    except Exception as e:
        logger.exception(e)
        raise BFValidationError("获取班级数据失败！")

    # 使用时长标准值
    total_list = queryset.values_list("student_use_duration", flat=True)
    duration_std_val = compute_std_val(klass_data_obj.student_use_duration, total_list)
    ret_data["duration_std_val"] = duration_std_val

    # 教学进度标准值
    total_list = queryset.values_list("teaching_progress", flat=True)
    teach_progress_std_val = compute_std_val(klass_data_obj.teaching_progress, total_list)
    ret_data["teach_progress_std_val"] = teach_progress_std_val
    # 正确率标准值
    total_list = queryset.values_list("right_rate", flat=True)
    right_rate_std_val = compute_std_val(klass_data_obj.right_rate, total_list)
    ret_data["right_rate_std_val"] = right_rate_std_val
    # 成绩标准值
    total_list = queryset.values_list("score", flat=True)
    score_std_val = compute_std_val(klass_data_obj.score, total_list)
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
    use_num_std_val = compute_std_val(klass_data_obj.student_use_num, total_list)
    ret_data["use_num_std_val"] = use_num_std_val
    # 使用次数标准值
    total_list = queryset.values_list("task_num", flat=True)
    use_times_std_val = compute_std_val(klass_data_obj.task_num, total_list)
    ret_data["use_times_std_val"] = use_times_std_val
    # 交互次数标准值
    total_list = queryset.values_list("interactive_num", flat=True)
    interactive_num_std_val = compute_std_val(klass_data_obj.interactive_num, total_list)
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
    if klass_data_obj.student_num:
        use_num_ratio = float(klass_data_obj.student_use_num) / klass_data_obj.student_num
    else:
        use_num_ratio = 0
    use_num_ratio_std_val = compute_std_val(use_num_ratio, total_list)
    ret_data["use_num_ratio_std_val"] = use_num_ratio_std_val
    # 活动数量标准值
    total_list = queryset.values_list("activity_num", flat=True)
    activity_num_std_val = compute_std_val(klass_data_obj.activity_num, total_list)
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


def get_klass_stage_score(klass, term):
    """
    统计班级阶段成绩

    :param obj: 班级
    :param term: 学期
    :return:
    """
    ret_data = {}
    midterm_score = StageScore.objects.filter(term=term, klass_id=klass.id, score_type=1).values_list('score',
                                                                                                      flat=True)
    if len(midterm_score) > 0:
        ret_data['midterm_avg_score'] = np.mean(midterm_score)
        ret_data['midterm_max_score'] = np.max(midterm_score)
        ret_data['midterm_min_score'] = np.min(midterm_score)
        ret_data['midterm_lower_quartile'] = sts.quantile(midterm_score, p=0.75)
        ret_data['midterm_median'] = np.median(midterm_score)
        ret_data['midterm_upper_quartile'] = sts.quantile(midterm_score, p=0.25)
    fs_score = StageScore.objects.filter(term=term, klass_id=klass.id, score_type=2).values_list('score', flat=True)
    if len(midterm_score) > 0:
        ret_data['fs_avg_score'] = np.mean(fs_score)
        ret_data['fs_max_score'] = np.max(fs_score)
        ret_data['fs_min_score'] = np.min(fs_score)
        ret_data['fs_lower_quartile'] = sts.quantile(fs_score, p=0.75)
        ret_data['fs_median'] = np.median(fs_score)
        ret_data['fs_upper_quartile'] = sts.quantile(fs_score, p=0.25)
    fe_score = StageScore.objects.filter(term=term, klass_id=klass.id, score_type=3).values_list('score', flat=True)
    if len(midterm_score) > 0:
        ret_data['fe_avg_score'] = np.mean(fe_score)
        ret_data['fe_max_score'] = np.max(fe_score)
        ret_data['fe_min_score'] = np.min(fe_score)
        ret_data['fe_lower_quartile'] = sts.quantile(fe_score, p=0.75)
        ret_data['fe_median'] = np.median(fe_score)
        ret_data['fe_upper_quartile'] = sts.quantile(fe_score, p=0.25)
    return ret_data


if __name__ == '__main__':
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    kl = get_klass_list()
    write_to_klass_data(t, kl)
