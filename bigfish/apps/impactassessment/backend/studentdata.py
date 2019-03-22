import calendar
import datetime
import logging

from django.db.models.functions import Coalesce

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.visualbackend.backend.commons import get_current_school_week, get_user_basic_data, get_current_term, \
    get_current_week
from bigfish.apps.reports.models import SaveDataInfo, Conversation, SaveDataDetails
from bigfish.apps.users.models import UserProfile
from bigfish.apps.impactassessment.models import StudentWeekData, StudentMonthData
from django.db.models import Avg, Max, Min, Value, Sum, Count
from bigfish.apps.versus.models import VersusDetail

logger = logging.getLogger('backend')


def write_to_student_data(week, current_time):
    user_profile_list = UserProfile.objects.filter(identity='学生', attend_class__school__is_normal=True)
    write_to_student_week_data(week, user_profile_list)
    write_to_student_month_data(current_time.year, current_time.month, user_profile_list)


def write_to_student_week_data(week, user_profile_list):
    for user_profile in user_profile_list:
        print("==================================================", user_profile.user.username)
        # basic info
        basic_info = get_user_basic_data(user_profile)
        school_id = basic_info.get('school_id')
        school_week = get_current_school_week(school_id, week)
        if school_week:
            basic_info['school_week'] = school_week
            query_duration = [school_week.start_date, school_week.finish_date]
        else:
            query_duration = [week.start_date, week.finish_date]
        kwargs = {"term": week.term, "klass_id": basic_info.get("klass_id"), "username": basic_info.get("username")}
        # compute data
        compute_data = get_compute_data(user_profile.user, query_duration)
        if not StudentWeekData.objects.filter(**kwargs).exists():
            compute_data.update(basic_info)
        try:
            StudentWeekData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def write_to_student_month_data(year, month, user_profile_list):
    for user_profile in user_profile_list:
        print("==================================================", user_profile.user.username)
        # basic info
        basic_info = get_user_basic_data(user_profile)
        # ------------------月份数据
        kwargs = {"school_year": year, "school_month": month,
                  "klass_id": basic_info.get("klass_id"),
                  "username": basic_info.get("username")}
        # compute data
        _, month_range = calendar.monthrange(year, month)
        first_day = datetime.date(year=year, month=month, day=1)
        last_day = datetime.date(year=year, month=month, day=month_range)
        query_duration = [first_day, last_day]
        compute_data = get_compute_data(user_profile.user, query_duration)
        if not StudentMonthData.objects.filter(**kwargs).exists():
            compute_data.update(basic_info)
        try:
            StudentMonthData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def get_compute_data(user, query_duration):
    """
    计算函数

    right_rate       正确率
    max_score        最大成绩
    min_score        最小成绩
    avg_score        平均值
    use_duration     使用时长
    interactive_num  平均交互次数
    task_num         任务数

    :param user: user对象
    :param query_duration: 查询时间段
    :return:
    """
    ret_data = {}
    in_use = True
    queryset = SaveDataInfo.objects.filter(add_time__date__range=query_duration, user=user)
    if not queryset.exists():
        logger.info("==========================【{}】该用户未产生练习数据".format(user.username))
        score_info, right_rate, in_use = {"avg_score": 0, "max_score": 0, "min_score": 0}, 0, False
        use_duration, interactive_num, task_num = 0, 0, 0
    else:
        score_info = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, user=user, activity_first_type=2, is_complete=True, is_push=False
        ).aggregate(max_score=Coalesce(Max('score'), Value(0)),
                    min_score=Coalesce(Min('score'), Value(0)),
                    avg_score=Coalesce(Avg('score'), Value(0)))
        """
        完成的活动
        除"检测与复习"以外的练习活动数据
        """
        right_rate = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, user=user, activity_first_type=1, is_complete=True, is_push=False
        ).aggregate(data=Coalesce(Avg('right_rate'), Value(0))).get("data")
        """
        使用总时长
        """
        use_duration = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, user=user, is_push=False
        ).aggregate(data=Coalesce(Sum('all_time'), Value(0))).get("data")
        """
        总交互次数
        
        1.学习活动数据 交互次数
        2.练习活动数据 答题条数
        3.1V1对战数据 答题条数
        """
        man_machine_num = Conversation.objects.filter(
            enterstudy__start_time__date__range=query_duration, enterstudy__owner=user
        ).aggregate(data=Count('id')).get("data")
        in_exercise = SaveDataDetails.objects.filter(
            save_data__add_time__date__range=query_duration,
            save_data__user=user).aggregate(data=Count('id')).get('data')
        in_versus = VersusDetail.objects.filter(versus__start_time__date__range=query_duration,
                                                versus__pk_user=user).aggregate(data=Count('id')).get('data')
        interactive_num = man_machine_num + in_exercise + in_versus
        """
         任务数
        """
        task_num = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, user=user, is_push=False
        ).order_by('task_id').distinct().count()
    logger.info("right_rate===================={}".format(right_rate))
    ret_data["right_rate"] = right_rate
    ret_data["in_use"] = in_use
    ret_data["use_duration"] = use_duration
    ret_data["interactive_num"] = interactive_num
    ret_data["task_num"] = task_num
    ret_data.update(score_info)

    return ret_data


if __name__ == '__main__':
    """
    写入studentData表数据
    """
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    w = get_current_week(ct)

    write_to_student_data(w, ct)
