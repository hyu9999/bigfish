# Create your views here.

import logging

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.achievement.models import Achievement, UserAchievement, DESC_CHOICE
from bigfish.apps.textbooks.models import Lesson
from bigfish.apps.achievement.serializers import AchievementSerializer, UserAchievementSerializer
from bigfish.apps.textbooks.models import Activity
from bigfish.base import status, viewsets
from bigfish.utils.functions import generate_fields
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400

logger = logging.getLogger("django")


class AchievementViewSet(viewsets.ModelViewSet):
    """
    成就创建修改删除
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    @list_route(methods=["POST"])
    def get_achievement(self, request):
        """
        {"achievement":1,"if_task":1}

        """
        ret_data = request.data
        owner = request.user
        ret_data['owner'] = owner.id
        achievement_id = ret_data.get('achievement', None)
        try:
            achieve = Achievement.objects.get(id=achievement_id)
        except Exception as e:
            logger.info(e)
            return Response(rsp_msg_400("成就不存在！"), status=status.HTTP_200_OK)
        if_task = ret_data.get('if_task', 0)
        if not achieve.have_task_achieve and if_task:
            return Response(rsp_msg_400("不是任务下的成就！"), status=status.HTTP_200_OK)
        current_num = 0
        try:
            user_achieve = UserAchievement.objects.get(owner=owner, achievement=achievement_id, if_task=if_task)
        except Exception as e:
            user_achieve = None
            logger.info(e)
            all_need_num = achieve.all_need_num
            if all_need_num:
                current_num = 1
                progress = round(current_num / all_need_num, 2)
            else:
                progress = 1.0
        else:
            # 已经存在
            if user_achieve.progress == 1.0:
                return Response(rsp_msg_200(), status=status.HTTP_200_OK)
            all_need_num = user_achieve.achievement.all_need_num
            if all_need_num:
                current_num = user_achieve.current_num + 1
                progress = round(current_num / all_need_num, 2)
            else:
                progress = 1.0
        achieve_status = UserAchievement.get_status_by_progress(progress)
        ret_data['if_task'] = if_task
        ret_data['current_num'] = current_num
        ret_data['progress'] = progress
        ret_data['status'] = achieve_status
        # update data
        if user_achieve:
            user_achieve_serializer = UserAchievementSerializer(user_achieve, data=ret_data)
        else:
            user_achieve_serializer = UserAchievementSerializer(data=ret_data)
        user_achieve_serializer.is_valid()
        user_achieve_serializer.save()
        # 是否返回
        if progress == 1.0:
            achieve_data = user_achieve_serializer.data
        else:
            achieve_data = None
        data = {"result": "success", "code": 200, "detail": achieve_data}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    # @list_route(methods=["POST"])
    # def get_progress_achievement(self, request):
    #     """
    #     根据类lesson,unit，activity获取成就
    #         1:第1节课
    #             入参：{"lesson":"","activity":"","unit":""}
    #         2:爱上英语
    #             入参：{"unit":"1","activity":"1"}
    #     """
    #     unit = request.data.get('unit', '')
    #     lesson = request.data.get('lesson', '')
    #     activity = request.data.get('activity', '')
    #     if not all([unit, lesson, activity]):
    #         return Response(rsp_msg_400(error_msg='参数不能为空'), status=status.HTTP_200_OK)
    #     owner = request.user
    #     filter_dict = {'owner': owner}
    #     achievement_list = progress_achievement(unit, lesson, activity, filter_dict)
    #     data = {"result": "success", "code": 200, "detail": achievement_list}
    #     return Response(rsp_msg_200(msg=data), status=status.HTTP_200_OK)


class UserAchievementViewSet(viewsets.ModelViewSet):
    """
    成就创建修改删除
    """
    queryset = UserAchievement.objects.all()
    serializer_class = UserAchievementSerializer
    filter_fields = generate_fields(UserAchievement)

    @list_route()
    def get_personal_achievement(self, request):
        """
        获取个人成就信息
        参数： user=1
        """
        user_id = request.GET.get('user', None)
        try:
            owner = User.objects.get(id=user_id)
        except:
            return Response(rsp_msg_400('此用户不存在'), status=status.HTTP_200_OK)
        if_task = request.GET.get('if_task', False)
        ret_data = {'data': get_user_achieve_data(owner, if_task), 'progress': get_achieve_percent(owner, if_task),
                    'total_progress': get_total_achieve_percent(owner, if_task)}
        data = {"result": "success", "code": 200, "detail": ret_data}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)


def get_user_achieve_data(owner, if_task):
    ret_dict = {}
    achieve_list = Achievement.objects.all().order_by('id')
    for achieve in achieve_list:
        user_achieve_list = UserAchievement.objects.filter(owner=owner, achievement=achieve, if_task=if_task)
        if user_achieve_list.count() == 0:
            create_dict = {'status': 1, 'owner': owner, 'achievement': achieve, 'progress': 0.0,
                           'if_task': if_task}
            user_achieve = UserAchievement.objects.create(**create_dict)
        else:
            user_achieve = user_achieve_list[0]
        serializer = UserAchievementSerializer(user_achieve, many=False)
        if ret_dict.get(achieve.desc_type, None):
            ret_dict[achieve.desc_type].append(serializer.data)
        else:
            ret_dict[achieve.desc_type] = []

            ret_dict[achieve.desc_type].append(serializer.data)
    # order by status
    sort_dict = {}
    for k, v in ret_dict.items():
        tmp_list = []
        complete_list = [x for x in v if x['status'] == '3']
        uncomplete_list = [x for x in v if x['status'] != '3']
        tmp_list.extend(complete_list)
        tmp_list.extend(uncomplete_list)
        sort_dict[k] = tmp_list
    return sort_dict


def get_achieve_percent(owner, if_task):
    ret_list = []
    for desc in DESC_CHOICE:
        suc_cnt = UserAchievement.objects.filter(owner=owner, if_task=if_task, progress=1.0,
                                                 achievement__desc_type=desc[0]).count()
        total_cnt = Achievement.objects.filter(desc_type=desc[0]).count()
        try:
            percent = round(float(suc_cnt) / float(total_cnt), 2)
        except:
            percent = 0.0
        tmp_dict = {'name': desc[0], 'value': desc[1], 'progress': '{}/{}'.format(suc_cnt, total_cnt),
                    'percent': percent}
        ret_list.append(tmp_dict)
    return ret_list


def get_total_achieve_percent(owner, if_task):
    sum_suc = UserAchievement.objects.filter(owner=owner, if_task=if_task, progress=1.0).count()
    sum_num = Achievement.objects.all().count()
    sum_percent = round(float(sum_suc) / float(sum_num), 2)
    return {'progress': '{}/{}'.format(sum_suc, sum_num), 'percent': sum_percent}


# def progress_achievement(unit, lesson, activity, filter_dict):  # 进度
#     return_list = []
#     return_list.extend(first_lesson(lesson, activity, filter_dict))
#     return_list.extend(full_in_love_with_english(unit, activity, filter_dict))
#     return return_list


def modify_achievement(filter_dict, name='第1节课'):
    try:
        achievement = Achievement.objects.get(name=name)
    except:
        return None
    filter_dict['achievement'] = achievement
    user_achievement = UserAchievement.objects.filter(
        **{'owner': filter_dict['owner'], 'achievement': achievement.id, 'if_task': filter_dict.get('if_task', 0)})
    if user_achievement.exists():
        obj = user_achievement[0]
        if obj.progress == 1.0:
            return None
        else:
            user_achievement.update(**filter_dict)
            achieve_progress = filter_dict.get('progress', None)
            if achieve_progress == 1.0:
                return get_fmt_data(obj)
            else:
                return None

    else:
        obj = UserAchievement.objects.create(**filter_dict)
        if float(obj.progress) == 1.0:
            return get_fmt_data(obj)
        else:
            return []


def get_fmt_data(obj):
    ret_dict = UserAchievementSerializer(obj).data
    ret_dict.pop('name', None)
    achievement_id = ret_dict['achievement']
    try:
        achievement = Achievement.objects.get(id=achievement_id)
    except:
        return []
    achievement_data = AchievementSerializer(achievement).data
    achievement_data.pop('id', None)
    ret_dict.update(achievement_data)
    return ret_dict

# def first_lesson(lesson, activity, filter_dict):
#     # 第1节课(自主课堂中，有1个Lesson进度达到100%)
#     # cnt_num = Activity.objects.filter(lesson=lesson).exclude(pointer='student_test').count()
#     # cnt_num_100 = Activityprogress.objects.filter(all_times__gte=1, lesson=lesson,
#     #                                               task_id="", user=filter_dict['owner']).exclude(
#     #     activity__pointer='student_test').count()
#     cnt_num = Activity.objects.control().filter(lesson=lesson).exclude(en_title="Warm up").count()
#     cnt_num_100 = Activityprogress.objects.filter(all_times__gte=1, lesson=lesson,
#                                                   task_id="", user=filter_dict['owner']).count()
#     #   练习
#     try:
#         progress = round(float(cnt_num_100) / float(cnt_num), 2)
#     except:
#         progress = 0.0
#     if progress == None:
#         progress = 0.0
#     status = UserAchievement.get_status_by_progress(progress)
#     practice_filter = {'progress': progress, 'status': status, 'if_task': 0}
#     practice_filter.update(filter_dict)
#     practice_obj = modify_achievement(practice_filter)
#     #   任务
#     try:
#         lesson = Activity.objects.control().get(id=activity).lesson
#     except:
#         return []
#     try:
#         cnt_num_task_100 = Activityprogress.objects.filter(~Q(task_id=""), all_times__gte=1,
#                                                            lesson=lesson, user=filter_dict['owner']).count()
#     except Exception as e:
#         cnt_num_task_100 = 0
#
#     try:
#         progress = round(float(cnt_num_task_100) / float(cnt_num), 2)
#     except:
#         progress = 0.0
#     status = UserAchievement.get_status_by_progress(progress)
#     task_filter = {'progress': progress, 'status': status, 'if_task': 1}
#     task_filter.update(filter_dict)
#     task_obj = modify_achievement(task_filter)
#     if [x for x in [practice_obj, task_obj] if x]:
#         ret_list = [x for x in [practice_obj, task_obj] if x]
#     else:
#         ret_list = []
#     return ret_list
#
#
# def full_in_love_with_english(unit, activity, filter_dict):
#     # 爱上英语(自主课堂中，有1个Unit进度达到100%)
#     # lesson_list = Lesson.objects.filter(~Q(pointer='student_test'), unit=unit)
#     # cnt_num = Activity.objects.filter(lesson__in=lesson_list).exclude(pointer='student_test').count()
#     # cnt_num_100 = Activityprogress.objects.filter(all_times__gte=1, lesson__in=lesson_list, task_id="",
#     #                                               user=filter_dict['owner']).exclude(
#     #     Q(activity__pointer='student_test')).count()
#     lesson_list = Lesson.objects.filter(unit=unit).exclude(pointer='student_test')
#     cnt_num = Activity.objects.control().filter(lesson__in=lesson_list).exclude(en_title="Warm up").count()
#     cnt_num_100 = Activityprogress.objects.filter(all_times__gte=1, lesson__in=lesson_list, task_id="",
#                                                   user=filter_dict['owner']).exclude(activity__en_title="Warm up") \
#         .count()
#     #   练习
#     try:
#         progress = round(float(cnt_num_100) / float(cnt_num), 2)
#     except:
#         progress = 0.0
#     status = UserAchievement.get_status_by_progress(progress)
#     practice_filter = {'progress': progress, 'status': status, 'if_task': 0}
#     practice_filter.update(filter_dict)
#     practice_obj = modify_achievement(practice_filter, name='爱上英语')
#     #   任务
#     # if unit == "":
#     #     try:
#     #         unit = Activity.objects.get(id=activity).lesson.unit
#     #     except:
#     #         return []
#     # cnt_num_task_100 = Activityprogress.objects.filter(~Q(task_id=""), all_times__gte=1,
#     #                                                    lesson__in=lesson_list, user=filter_dict['owner']).exclude(
#     #     activity__pointer='student_test').count()
#     cnt_num_task_100 = Activityprogress.objects.filter(~Q(task_id=""), all_times__gte=1,
#                                                        lesson__in=lesson_list, user=filter_dict['owner']) \
#         .exclude(activity__en_title="Warm up").count()
#     try:
#         progress = round(float(cnt_num_task_100) / float(cnt_num), 2)
#     except:
#         progress = 0.0
#     status = UserAchievement.get_status_by_progress(progress)
#     task_filter = {'progress': progress, 'status': status, 'if_task': 1}
#     task_filter.update(filter_dict)
#     task_obj = modify_achievement(task_filter)
#     if [x for x in [practice_obj, task_obj] if x]:
#         ret_list = [x for x in [practice_obj, task_obj] if x]
#     else:
#         ret_list = []
#     return ret_list
