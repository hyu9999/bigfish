import copy
import logging
from datetime import datetime

from django.core.cache import cache
from django.db.models import Sum
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bigfish.apps.classrooms.models import ActivityReport, Classroom, ActivityDetailReport, StuActivity
from bigfish.apps.operation.models import OperationRecord
from bigfish.apps.operation.views import create_or_update_operate
from bigfish.apps.resources.models import ActImage
from bigfish.apps.schools.models import Klass, KlassProgress, KlassActProgress
from bigfish.apps.textbooks.backend.operate_json import simple_act_rule
from bigfish.apps.textbooks.filters import LessonFilter, UnitFilter
from bigfish.apps.textbooks.models import Unit, Lesson, Textbook, Activity, PublishVersion, ActTab, \
    ActType, PrepareAdvise
from bigfish.apps.textbooks.serializers import UnitSerializer, LessonSerializer, TextbookSerializer, \
    PublishVersionSerializer, \
    ActivitySerializer, ActTabSerializer, ActTypeSerializer, PrepareAdviseMinSerializer, \
    TextbookCascadeSerializer, LessonDescriptionSerializer
from bigfish.apps.users.models import UserKlassRelationship, UserCourse
from bigfish.base import viewsets, status
from bigfish.base.const import TEACHER, STUDENT
from bigfish.base.public_db_data import get_question_report, get_question_data, get_act_data, get_publish_data, \
    get_user_data
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400, rsp_msg

logger = logging.getLogger("django")


class PublishVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = PublishVersion.objects.all().order_by('order')
    serializer_class = PublishVersionSerializer


class TextbookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    教材列表
    """
    queryset = Textbook.objects.all().order_by('grade')
    serializer_class = TextbookSerializer
    filter_fields = ('is_active', 'publish')

    @list_route(methods=['GET'])
    def get_user_textbook(self, request):
        """
        获取用户班级（未指定则为默认班级）教材列表

        :param request: \n
            [klass_id=1]
        :return:
        """
        user = request.user
        klass_id = request.query_params.get("klass_id", None)
        if klass_id:
            try:
                klass = Klass.objects.get(id=klass_id)
            except Exception as e:
                raise BFValidationError("班级不存在")

        else:
            try:
                klass = UserKlassRelationship.objects.get(user=user, is_effect=True, is_default=True).klass
            except Exception as e:
                raise BFValidationError("查询默认班级失败{}".format(e))
        if not klass.publish:
            raise BFValidationError("获取教材信息失败")
        queryset = Textbook.objects.filter(publish=klass.publish,
                                           is_active=True, grade__lte=klass.grade).order_by('grade', 'term')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TextbookCascadeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TextbookCascadeSerializer(queryset, many=True)

        return Response(serializer.data)


class ActTabViewSet(viewsets.ModelViewSet):
    """
    活动页签
    """
    queryset = ActTab.objects.all().order_by('order')
    serializer_class = ActTabSerializer
    filter_fields = ('id',)

    @list_route(methods=['GET'])
    def get_act_home_page(self, request):
        """
        活动首页

        :param request:

            request_type=app  or request_type=pc  (请求来源)

        :return:
        """
        user = request.user
        request_type = request.GET.get('request_type')
        result = []
        # 获取默认班级
        try:
            klass = UserKlassRelationship.objects.get(user=user, is_effect=True, is_default=True).klass
        except Exception as e:
            logger.debug(e)
            raise BFValidationError("无默认班级")
        # 分角色获取教材进度
        if user.identity == TEACHER:
            try:
                textbook_progress = KlassProgress.objects.get(klass=klass)
                lesson = textbook_progress.lesson
            except Exception as e:
                logger.error(e)
                return Response(rsp_msg(msg="未查询到班级教材进度", code=status.HTTP_600_NO_DATA))
        else:
            try:
                textbook_progress = UserCourse.objects.get(user=user)
                lesson = textbook_progress.lesson
            except Exception as e:
                logger.error(e)
                return Response(rsp_msg(msg="未查询到班级教材进度", code=status.HTTP_600_NO_DATA))
        if lesson is None:
            return Response(rsp_msg(msg="默认课程为空", code=status.HTTP_600_NO_DATA))
        # 拼接课程展示数据
        act_tab_queryset = ActTab.objects.all().order_by('order')
        for act_tab in act_tab_queryset:
            # 获取标签下活动
            activity_queryset = Activity.objects.filter(lesson=lesson,
                                                        act_tab_id=act_tab.id, is_active=True).order_by('order')
            # 标签下有活动 才会返回标签
            if activity_queryset.exists():
                act_tab_list = []
                try:
                    pc_image = act_tab.pc_image.res.url
                    app_image = act_tab.app_image.res.url
                except Exception as e:
                    logger.error('活动页签pc_image: {}'.format(e))
                    pc_image = ''
                    app_image = ''
                tab_data = {'act_tab_name': act_tab.title, 'act_tab_id': act_tab.id, 'act_data': act_tab_list,
                            'pc_image': pc_image, 'app_image': app_image}
                for activity in activity_queryset:
                    try:
                        activity_image = activity.image.res.url
                    except Exception as e:
                        logger.error('活动activity_image: {}'.format(e))
                        activity_image = ''
                    activity_data = {'activity_id': activity.id, 'activity_title': activity.title,
                                     'activity_image': activity_image, "display_type": activity.display_type,
                                     'prepare_advise_id': activity.prepare_advise_id}
                    act_tab_list.append(activity_data)
                result.append(tab_data)
        if request_type == 'app':
            # 添加1v1， 课堂巩固
            pass
            # image = Image.objects.get(id=4)
            # fight_data = {
            #     "pc_image": image.res.url,
            #     "act_tab_name": "1v1对战",
            #     "act_tab_id": -1,
            #     "app_image": image.res.url,
            #     "act_data": [
            #         {
            #             "activity_id": -1,
            #             "activity_title": "1v1对战",
            #             "activity_image": image.res.url,
            #             "display_type": 100
            #         }
            #     ]
            # }
            #
            # result.append(fight_data)
            # image = Image.objects.get(id=4)
            # classroom_data = {
            #     "pc_image": image.res.url,
            #     "act_tab_name": "课堂知识巩固",
            #     "act_tab_id": -2,
            #     "app_image": image.res.url,
            #     "act_data": [
            #         {
            #             "activity_id": -2,
            #             "activity_title": "课堂知识巩固",
            #             "activity_image": image.res.url,
            #             "display_type": 101
            #         }
            #     ]
            # }
            # result.append(classroom_data)
        elif request_type == 'pc':
            pass
        # 活动底部标题
        act_bottom_title = ' '.join([lesson.unit.textbook.title, lesson.unit.en_title, lesson.en_title])
        # 课程引导视频
        try:
            video_url = lesson.unit.video.res.url
        except Exception as e:
            logger.debug(e)
            video_url = ""
        results = {'act_in': result, 'act_bottom_title': act_bottom_title, "video": video_url, "lesson_id": lesson.id}
        return Response(rsp_msg_200(results), status=status.HTTP_200_OK)


class ActTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = ActType.objects.all()
    serializer_class = ActTypeSerializer


class PrepareAdviseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = PrepareAdvise.objects.all()
    serializer_class = PrepareAdviseMinSerializer


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    活动列表信息
    """
    queryset = Activity.objects.all().order_by('order')
    serializer_class = ActivitySerializer
    filter_fields = ('lesson__id', 'act_tab')

    @list_route(methods=['GET'])
    def activity_rule_data(self, request):
        """
        根据活动ID获取规则信息
        :param request: \n
            activity_id：1   #活动id
            classroom_id：1  #课堂id
        :return: \n
        """

        activity_id = request.query_params.get('activity_id', None)
        if activity_id is None:
            return Response(rsp_msg_400('请传入活动ID！'), status=status.HTTP_200_OK)
        try:
            act = Activity.objects.get(id=activity_id)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400('传入的活动ID有误，请查证！'), status=status.HTTP_200_OK)
        data = cache.get("activity_rule_data_{}".format(activity_id))
        if data:
            return Response(rsp_msg_200(data), status=status.HTTP_200_OK)
        # ret_data = act.rule_data
        ret_data = simple_act_rule(act.rule)
        try:
            act_image_obj = ActImage.objects.get(activity_name=act.title)
        except Exception as e:
            act_image = ""
        else:
            act_image = act_image_obj.image.res.url
        ret_data["act_image"] = act_image

        cache.set("activity_rule_data_{}".format(activity_id), ret_data, timeout=None)
        # # cur_classroom = get_cur_classroom(request.user)
        # classroom_id = request.data.get("classroom_id", None)
        # # update classroom latest_lesson/latest_act/lesson
        # if classroom_id:
        #     try:
        #         cur_classroom = Classroom.objects.get(id=classroom_id)
        #     except Exception as e:
        #         logger.info(e)
        #         return Response(rsp_msg_400('传入的课堂ID有误，请查证！'), status=status.HTTP_200_OK)
        #     cur_classroom.latest_lesson = act.lesson
        #     cur_classroom.latest_act_id = activity_id
        #     queryset = cur_classroom.lesson.filter(id=act.lesson_id)
        #     if not queryset.exists():
        #         cur_classroom.lesson.add(act.lesson)
        #     cur_classroom.save()

        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)

    def get_act_report(self, request, activity):
        """活动概要数据"""
        user = request.user
        act_report = {
            'activity': activity,
            'unit': activity.unit,
            'lesson': activity.lesson,
            'user': user,
            'is_push': request.data.get('is_push', False),
            'scene': request.data.get('scene', 0)
        }
        return act_report

    def get_student_act_data(self, request, activity):
        """课堂学生完成活动情况数据"""
        user = request.user
        classroom_id = request.data.get('classroom_id', None)
        max_score = request.data.get('score')
        try:
            stu_act = StuActivity.objects.get(user=user, activity=activity, classroom_id=classroom_id)
            max_score = max(stu_act.max_score, max_score)
        except:
            pass
            max_score = max_score
        user_klass = UserKlassRelationship.objects.filter(klass__in=user.attend_class.all(), user__identity=1).first()
        # 记录课堂活动情况时 活动概要表还没有进行记录 次数需要+1
        activity_queryset = ActivityReport.objects.filter(classroom_id=classroom_id,
                                                          activity=activity, user=user)
        entry_times = activity_queryset.count()
        if entry_times == 0:
            entry_times = 1
        sum_score = activity_queryset.aggregate(sum_score=Sum('score')).get('sum_score') or 0
        stu_act_data = {
            'teacher': user_klass.user,
            'progress': request.data.get('progress', 0),
            'max_score': max_score,
            'avg_score': '%.2f' % (sum_score / entry_times),
            'latest_score': request.data.get('score', 0),
            'entry_times': entry_times + 1,
            'is_finish': request.data.get('is_finish', False),
        }
        return stu_act_data

    @list_route(methods=['POST'])
    def save_act_data(self, request):
        """
        存储活动数据
        :param request:
        :return:
        """
        user = request.user
        classroom_id = request.data.get('classroom_id', 0)
        act_report_id = request.data.get('act_report_id', 0)
        activity_id = request.data.get('activity_id', None)
        try:
            activity = Activity.objects.get(id=activity_id)
        except:
            return Response(rsp_msg_400('活动id有误'))
        # 获取存储数据
        questin_data = get_question_data(request)
        question_report = get_question_report(request)
        act_data = get_act_data(activity)
        publish_data = get_publish_data(activity)
        user_data = get_user_data(request)

        act_report = self.get_act_report(request, activity)
        # 概要数据
        act_report_data = {**act_data, **questin_data, **publish_data, **user_data, **act_report}
        # 详情数据
        act_detail_report_data = copy.deepcopy(act_report_data)
        act_detail_report_data.update(**question_report)
        if classroom_id != 0:
            try:
                classroom = Classroom.objects.get(id=classroom_id)
            except:
                return Response(rsp_msg_400('课堂id有误'))
            else:
                act_report_data.update({'classroom': classroom})
                act_detail_report_data.update({'classroom': classroom})
            # 课堂学生完成活动情况记录
            if user.identity == STUDENT:
                stu_act_data = self.get_student_act_data(request, activity)
                stu_act_data.update(act_report_data)
                defaults = {'classroom': classroom, 'user': user, 'activity': activity}
                StuActivity.objects.update_or_create(defaults=stu_act_data, **defaults)
        # 第一题
        if act_report_id == 0:
            # 创建活动概要数据
            act_report = ActivityReport.objects.create(**act_report_data)
            act_detail_report_data.update({'activity_report': act_report})
            # 创建活动详情数据
            ActivityDetailReport.objects.create(**act_detail_report_data)
            return Response(rsp_msg_200({'act_report_id': act_report.id}), status=status.HTTP_200_OK)
        else:
            # 更新活动记录概要数据
            questin_data = get_question_data(request)
            questin_data['all_time'] += request.data.get('all_time', 0)
            ActivityReport.objects.filter(id=act_report_id).update(**questin_data)
            # 创建活动记录详情数据
            act_detail_report_data.update({'activity_report_id': act_report_id})
            ActivityDetailReport.objects.create(**act_detail_report_data)
            return Response(rsp_msg_200(), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def publish_activity(self, request):
        """
        发布活动 (创建开始操作记录)
        :param request:
        
            {
                "classroom_id": 1,
                "klass_id": 1,
                "activity_id": 1,
                "start_time": ""
            }
        :return:

            {"operation_record_id": 1}
        """
        user = request.user
        classroom_id = request.data.get('classroom_id', None)
        act_id = request.data.get('activity_id', None)
        klass_id = request.data.get('klass_id', None)
        start_time = request.data.get('start_time', None)
        if not all([classroom_id, act_id, start_time]):
            return Response(rsp_msg_400('参数有误'), status=status.HTTP_200_OK)
        try:
            activity = Activity.objects.get(id=act_id)
        except:
            return Response(rsp_msg_400('活动id不存在'), status=status.HTTP_200_OK)
        # 记录发布活动行为
        operate_data = {
            "classroom_id": classroom_id,  # 课堂必填
            "operate_type_id": 1,  # 操作类型  1: 课堂操作
            "operation_id": 1,  # 操作行为ID 1：
            "operate_id": act_id,  # 操作内容ID(活动ID,课堂ID等)  根据类型记录不同id
        }
        dict_param = {
            "scene": 2,  # 场景
            "is_finish": request.data.get('is_finish', False),  # 是否结束
            "start_time": start_time,
            "finish_time": start_time,
            "klass_id": klass_id
        }
        operation_record = create_or_update_operate(user, activity.lesson, dict_param, operate_data)
        return Response(rsp_msg_200({"operation_record_id": operation_record.id}), status=status.HTTP_200_OK)

    def get_activity_report_data(self, request, classroom_id, activity, klass_id, operation_record):
        """
        获取活动统计数据
        :return:
        """
        finish_time = request.data.get('finish_time', None)
        finish_time = datetime.strptime(finish_time, '%Y-%m-%d %H:%M:%S')
        klass_student_num = UserKlassRelationship.objects.filter(klass_id=klass_id, user__identity=2).count()
        activity_report = ActivityReport.objects.filter(classroom_id=classroom_id,
                                                        activity=activity,
                                                        is_complete=True)
        # 没有记录活动数据
        if not activity_report.exists():
            dict_param = {
                "finish_num": 0,  # 完成人数
                "unfinished_num": klass_student_num,  # 未完成人数
                "has_score": False,  # 是否有成绩
                "avg_score": 0,  # 平均分
                "is_finish": True,  # 是否结束
                "duration": (finish_time - operation_record.start_time).total_seconds(),  # 时长 单位（秒）
                "finish_time": finish_time,
            }
            return dict_param
        finish_num = activity_report.distinct('user').count()
        sum_score = activity_report.aggregate(sum_score=Sum('score'))['sum_score']
        if activity.act_type.first_type == 2:
            has_score = False
            avg_score = 0.0
        else:
            has_score = True
            avg_score = '%.2f' % (sum_score / activity_report.count())
        dict_param = {
            "finish_num": finish_num,  # 完成人数
            "unfinished_num": klass_student_num - finish_num,  # 未完成人数
            "has_score": has_score,  # 是否有成绩
            "avg_score": avg_score,  # 平均分
            "is_finish": True,  # 是否结束
            "duration": (finish_time - operation_record.start_time).seconds,  # 时长 单位（秒）
            "finish_time": finish_time,
        }
        return dict_param

    @list_route(methods=['POST'])
    def finish_activity(self, request):
        """
        结束活动
        :param request:

            {
                "operation_record_id": 1,
                "finish_time": "2019-02-15 10:39:00",
            }
        :return: 
        """
        user = request.user
        finish_time_str = request.data.get('finish_time', None)
        finish_time = datetime.strptime(finish_time_str, '%Y-%m-%d %H:%M:%S')
        operation_record_id = request.data.get('operation_record_id', None)
        is_prepare = request.data.get("is_prepare", None)

        if not all([operation_record_id]):
            return Response(rsp_msg_400('参数有误'), status=status.HTTP_200_OK)
        try:
            operation_record = OperationRecord.objects.get(id=operation_record_id)
        except:
            return Response(rsp_msg_400('{}参数有误'.format(operation_record_id)), status=status.HTTP_200_OK)
        try:
            activity = Activity.objects.get(id=operation_record.operate_id)
        except:
            raise BFValidationError('活动id不存在')
        # 记录发布活动行为

        operate_data = {
            "classroom_id": operation_record.classroom_id,  # 课堂必填
            "operate_type_id": 1,  # 操作类型  1: 课堂操作
            "operation_id": 1,  # 操作行为ID 1：
            "operate_id": operation_record.operate_id,  # 操作内容ID(活动ID,课堂ID等)  根据类型记录不同id
            # 同一活动可能发布两次 需要进行区分
            "id": operation_record_id,
        }
        dict_param = self.get_activity_report_data(request, operation_record.classroom_id, activity,
                                                   operation_record.klass_id, operation_record)
        # 更新活动操作记录数据
        create_or_update_operate(user, activity.lesson, dict_param, operate_data)
        # 记录班级活动学习进度
        kwargs = {
            "klass_id": operation_record.klass_id,
            "activity_id": activity.id
        }
        time_duration = (finish_time - operation_record.start_time).total_seconds() * 1000
        defaults = {
            "time_duration": time_duration,
            "is_finish": True
        }
        if not is_prepare:
            update_klass_act_progress(defaults, kwargs)
        return Response(rsp_msg_200(), status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ModelViewSet):
    """
    课程列表
    """
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = LessonSerializer
    filter_fields = ('is_active', 'id', 'unit')
    filter_class = LessonFilter


class LessonDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    课程描述
    """
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = LessonDescriptionSerializer
    filter_fields = ('id',)
    permission_classes = (AllowAny,)


class UnitViewSet(viewsets.ModelViewSet):
    """
    单元列表
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filter_fields = ('is_active', 'id')
    filter_class = UnitFilter


def get_gif_path(base, obj):
    data_list = []
    gif_list = obj.split(",")
    for g in gif_list:
        path = base + g + '.gif'
        data_list.append(path)
    return data_list


def init_klass_act_progress(lesson_id, klass_id):
    """
    初始化班级活动进度

    :return:
    """
    if KlassActProgress.objects.filter(lesson_id=lesson_id, klass_id=klass_id).exists():
        return True
    act_list = Activity.objects.filter(lesson_id=lesson_id)
    sql_list = []
    for act_info in act_list:
        param_dict = {"klass_id": klass_id, "lesson_id": lesson_id, "act_tab_id": act_info.act_tab_id,
                      "activity_id": act_info.id, "suggested_time": act_info.suggested_time, "is_finish": False}
        tmp_data = KlassActProgress(**param_dict)
        sql_list.append(tmp_data)
    try:
        KlassActProgress.objects.bulk_create(sql_list)
    except Exception as e:
        logger.debug(e)
        raise BFValidationError("初始化班级活动失败")


def update_klass_act_progress(defaults, kwargs):
    """
    更新班级活动进度
    :param defaults:
        {
            "time_duration":1, # 修改使用时长
            "is_finish":True # 修改是否完成标识
            ...
        }
    :param kwargs:
        {
            "klass_id":1,
            "activity_id":1
        }
    :return:
    """
    try:
        KlassActProgress.objects.filter(**kwargs).update(**defaults)
    except Exception as e:
        logger.debug(e)
        return False
    else:
        return True
