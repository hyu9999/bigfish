import datetime
import logging

from django.db.models.functions import Coalesce

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.visualbackend.backend.commons import get_user_basic_data, get_current_school_term, get_current_term
from bigfish.apps.reports.models import SaveDataInfo, EnterStudy, Conversation, SaveDataDetails
from bigfish.apps.users.models import UserProfile
from bigfish.apps.versus.models import Versus, VersusDetail
from bigfish.apps.visualbackend.models import StudentData
from django.db.models import Avg, Sum, F, Count, Value

logger = logging.getLogger('backend')


def write_to_student_data(term):
    # student list
    user_list = UserProfile.objects.filter(identity='学生', attend_class__school__is_normal=True)
    for user_profile in user_list:
        print("==================================================", user_profile.user.username)
        # basic info
        basic_info = get_user_basic_data(user_profile)
        kwargs = {"term": term, "klass_id": basic_info.get("klass_id"), "username": basic_info.get("username")}
        school_id = basic_info.get('school_id')
        school_term = get_current_school_term(school_id, term)
        if school_term:
            basic_info['school_term'] = school_term
            query_duration = [school_term.start_date, school_term.finish_date]
        else:
            query_duration = [term.start_date, term.finish_date]
        # compute data
        compute_data = get_compute_data(user_profile.user, query_duration)

        if not StudentData.objects.filter(**kwargs).exists():
            compute_data.update(basic_info)
        try:
            StudentData.objects.update_or_create(defaults=compute_data, **kwargs)
        except Exception as e:
            logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def get_compute_data(user, query_duration):
    ret_data = {}
    in_use = True
    queryset = SaveDataInfo.objects.filter(add_time__date__range=query_duration, user=user)
    if not queryset.exists():
        logger.info("==========================【{}】该用户未产生练习数据".format(user.username))
        score, right_rate, exercise_num, in_use = 0, 0, 0, False
    else:
        """
        完成的活动
        1."检测与复习"下的所有活动的练习数据
        2.期中考试成绩——需要手动录入，需要确定录入字段
        3.期末考试成绩——需要手动录入，需要确定录入字段
        """
        score = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, user=user, activity_first_type=2,
            is_complete=True, is_push=False).aggregate(data=Coalesce(Avg('score'), Value(0))).get("data")
        """
        完成的活动
        除"检测与复习"以外的练习活动数据
        """
        right_rate = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, user=user, activity_first_type=1,
            is_complete=True, is_push=False).aggregate(data=Coalesce(Avg('right_rate'), Value(0))).get("data")
        """
        练习活动产生的数据
        """
        exercise_num = SaveDataInfo.objects.filter(
            add_time__date__range=query_duration, is_push=False, user=user).aggregate(
            data=Count('id')).get("data")
    logger.info("score===================={}".format(score))
    ret_data["score"] = score
    logger.info("right_rate===================={}".format(right_rate))
    ret_data["right_rate"] = right_rate
    use_duration = get_use_duration(user, query_duration)
    logger.info("use_duration===================={}".format(use_duration))
    ret_data["use_duration"] = use_duration
    logger.info("exercise_num===================={}".format(exercise_num))
    ret_data["exercise_num"] = exercise_num
    ret_data["in_use"] = in_use

    """
    学习活动交互次数累加
    """
    man_machine_num = Conversation.objects.filter(
        enterstudy__start_time__date__range=query_duration,
        enterstudy__owner=user).aggregate(data=Count('id')).get("data")
    ret_data["man_machine_num"] = man_machine_num
    logger.info("man_machine_num===================={}".format(man_machine_num))
    interactive_num = get_interactive_num(user, query_duration, man_machine_num)
    ret_data["interactive_num"] = interactive_num
    logger.info("interactive_num===================={}".format(interactive_num))
    """
    所有活动
    """
    activity_num = get_activity_num(user, query_duration)
    ret_data["activity_num"] = activity_num
    logger.info("activity_num===================={}".format(activity_num))
    return ret_data


def get_use_duration(user, query_duration):
    """
    1.学习活动数据
    2.练习活动数据
    3.1V1对战数据
    以上数据中的总用时累加
    """
    ud_study = SaveDataInfo.objects.filter(
        add_time__date__range=query_duration, is_push=False, user=user).aggregate(
        data=Coalesce(Sum('all_time'), Value(0))).get("data")
    ud_exercise = EnterStudy.objects.filter(
        start_time__date__range=query_duration, owner=user).aggregate(
        data=Coalesce(Sum(F('end_time') - F('start_time')), Value(datetime.timedelta(seconds=0)))).get("data")
    ud_exercise = ud_exercise.total_seconds()
    ud_versus = Versus.objects.filter(
        start_time__date__range=query_duration, pk_user=user).aggregate(
        data=Coalesce(Sum(F('end_time') - F('start_time')), Value(datetime.timedelta(seconds=0)))).get("data")
    ud_versus = ud_versus.total_seconds()
    use_duration = ud_study + ud_exercise + ud_versus
    return use_duration


def get_interactive_num(user, query_duration, man_machine_num):
    """
    1.学习活动数据 交互次数
    2.练习活动数据 答题条数
    3.1V1对战数据 答题条数
    以上数据中的条数累加
    """
    in_exercise = SaveDataDetails.objects.filter(
        save_data__add_time__date__range=query_duration,
        save_data__user=user).aggregate(data=Count('id')).get('data')
    in_versus = VersusDetail.objects.filter(versus__start_time__date__range=query_duration,
                                            versus__pk_user=user).aggregate(data=Count('id')).get('data')
    interactive_num = man_machine_num + in_exercise + in_versus
    return interactive_num


def get_activity_num(user, query_duration):
    """
    所有活动
    """
    an_study = EnterStudy.objects.filter(start_time__date__range=query_duration,
                                         owner=user).aggregate(data=Count('id')).get("data")
    an_exercise = SaveDataInfo.objects.filter(add_time__date__range=query_duration, is_push=False,
                                              user=user).aggregate(data=Count('id')).get("data")
    activity_num = an_study + an_exercise
    return activity_num


# def update_klass_id():
#     term = get_current_term()
#     sdi = SaveDataInfo.objects.filter(add_time__date__range=[term.start_date, term.finish_date], is_push=False,
#                                       klass_id=0)
#     for obj in sdi:
#         klass_id = obj.user.profile.default_cid
#         if klass_id:
#             print("klass==[{}]".format(klass_id))
#             obj.klass_id = klass_id
#             obj.save()


if __name__ == '__main__':
    """
    写入studentData表数据
    """
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    write_to_student_data(t)
