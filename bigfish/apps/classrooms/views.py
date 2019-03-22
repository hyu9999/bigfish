import logging
import datetime

from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.classrooms.models import BlackSetting, BlackSettingReport, Cast, CastReport, Classroom, \
    ActivityReport, ActivityDetailReport
from bigfish.apps.classrooms.serializers import BlackSettingSerializer, BlackSettingReportSerializer, CastSerializer, \
    CastReportSerializer, ClassroomSerializer, \
    ActivityReportSerializer, ActivityDetailReportSerializer
from bigfish.apps.operation.models import OperationRecord
from bigfish.apps.schools.models import Klass, KlassProgress
from bigfish.apps.textbooks.models import Activity
from bigfish.apps.users.models import UserKlassRelationship
from bigfish.apps.operation.views import create_or_update_operate
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400
from bigfish.base.permissions import OnlyTeacher

logger = logging.getLogger('django')


class BlackSettingViewSet(viewsets.ModelViewSet):
    """
    黑屏创建修改删除
    """
    queryset = BlackSetting.objects.all()
    serializer_class = BlackSettingSerializer
    # permission_classes = (OnlyTeacher,)
    filter_fields = ('klass__id',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(rsp_msg_200(), status=status.HTTP_200_OK, headers=headers)

    def black_setting_operate_data(self, user, request, klass_id, operate_data):
        """黑屏操作记录"""
        try:
            klass_progress = KlassProgress.objects.get(klass_id=klass_id)
        except:
            return Response(rsp_msg_400('班级信息有误'), status=status.HTTP_200_OK)
        operate_data = operate_data
        cur_time = datetime.datetime.now()
        dict_param = {
            "scene": 2,  # 场景
            "is_finish": request.data.get('is_finish', False),  # 是否结束
            "duration": request.data.get('duration', 0),  # 时长
            "start_time": cur_time,
            "finish_time": request.data.get('finish_time', cur_time),
        }
        operation_record = create_or_update_operate(user, klass_progress.lesson, dict_param, operate_data)
        return operation_record

    @list_route(methods=['PUT'], permission_classes=((OnlyTeacher,)))
    def change_black_setting_status(self, request):
        """
         黑屏设置

        :param request:

            {
                "is_black": false,
                "klass_id": "1",
                "classroom_id": 1,
                "operation_record_id": 1,               # 操作记录id  开启黑屏不穿 关闭传
                "finish_time": "",                       # 关闭黑屏时间  开启不传
                "duration": 0,                          # 黑屏时长
                "is_finish": false                       # 是否结束
            }
        :return:
        """

        user = request.user
        klass_id = request.data.get("klass_id", None)
        classroom_id = request.data.get('classroom_id', None)
        is_black = request.data.get("is_black", None)
        operation_record_id = request.data.get('operation_record_id', None)
        if classroom_id is None:
            return Response(rsp_msg_400(msg="请传入课堂id"), status=status.HTTP_200_OK)
        all_class_id = list(user.attend_class.all().values_list('id', flat=True))
        if klass_id not in all_class_id:
            return Response(rsp_msg_400(msg="不在当前班级，无权限修改黑屏状态！"), status=status.HTTP_200_OK)

        bs_obj = BlackSetting.objects.filter(klass_id=klass_id)
        # add
        if not bs_obj.exists():
            create_parmas = {
                'user': user,
                'klass_id': klass_id,
                'is_black': is_black
            }
            black_setting = BlackSetting.objects.create(**create_parmas)

        else:
            # update
            update_data = {'is_black': is_black}
            bs_obj.update(**update_data)
            black_setting = bs_obj[0]
        # 记录操作行为
        if is_black:
            operate_data = {
                "classroom_id": classroom_id,  # 课堂必填
                "operate_type_id": 1,  # 操作类型  1: 课堂操作
                "operation_id": 3,  # 操作行为ID 1：
                "operate_id": black_setting.id,  # 操作内容ID(活动ID,课堂ID等)  根据类型记录不同id
            }
            operation_record = self.black_setting_operate_data(user, request, klass_id, operate_data)
            return Response(rsp_msg_200({"operation_record_id": operation_record.id}), status=status.HTTP_200_OK)
        else:
            # 关闭黑屏 根据id进行更新操作数据
            operate_data = {
                "id": operation_record_id
            }
            operation_record = self.black_setting_operate_data(user, request, klass_id, operate_data)
            return Response(rsp_msg_200({"operation_record_id": operation_record.id}), status=status.HTTP_200_OK)


class BlackSettingReportViewSet(viewsets.ModelViewSet):
    queryset = BlackSettingReport.objects.all()
    serializer_class = BlackSettingReportSerializer
    filter_fields = ('klass__id',)


class CastViewSet(viewsets.ModelViewSet):
    queryset = Cast.objects.all()
    serializer_class = CastSerializer
    filter_fields = ('klass__id',)


class CastReportViewSet(viewsets.ModelViewSet):
    queryset = CastReport.objects.all()
    serializer_class = CastReportSerializer
    filter_fields = ('klass__id',)


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    filter_fields = {
        "id": ["exact"],
        "opener": ["exact"],
        "identity": ["exact"],
        "klass": ["exact"],
        "latest_lesson": ["exact"],
        "latest_act": ["exact"],
        "is_prepare": ["exact"],
        "is_open": ["exact"],
    }

    def create(self, request, *args, **kwargs):
        user = request.user
        change_klass = request.data.get('change_klass', False)
        klass_id = request.data.get('klass', None)
        if change_klass:
            if klass_id is None:
                return Response(rsp_msg_400('请传入要修改的班级id'), status=status.HTTP_200_OK)
            try:
                user_klass = UserKlassRelationship.objects.get(user=user, is_default=True,
                                                               is_effect=True)

                #  传入不是默认班级 就进行修改
                if not user_klass.klass.id == klass_id:
                    user_klass.is_default = False
                    user_klass.save()
                    try:
                        UserKlassRelationship.objects.filter(user=user,
                                                             klass_id=klass_id, is_effect=True).update(
                            **{'is_default': True})
                    except:
                        return Response(rsp_msg_400('班级不存在'), status=status.HTTP_200_OK)
            except Exception as e:
                logger.debug(e)
                # return Response(rsp_msg_400('用户默认班级有误'), status=status.HTTP_200_OK)
                try:
                    UserKlassRelationship.objects.filter(user=user,
                                                         klass_id=klass_id, is_effect=True).update(
                        **{'is_default': True})
                except:
                    return Response(rsp_msg_400('班级不存在'), status=status.HTTP_200_OK)

        try:
            klass = KlassProgress.objects.get(klass_id=klass_id)
            lesson = klass.lesson
        except:
            lesson = None
        # request.data['record_date'] = date.today()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            raise BFValidationError(serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        classroom_id = serializer.data['id']

        result = {"classroom_id": classroom_id}
        # 记录操作行为
        operate_data = {
            "classroom_id": classroom_id,  # 课堂必填
            "operate_type_id": 1,  # 操作类型  1: 课堂操作
            "operation_id": 3,  # 操作行为ID 1：
            "operate_id": classroom_id,  # 操作内容ID(活动ID,课堂ID等)  根据类型记录不同id
        }
        cur_time = datetime.datetime.now()
        dict_param = {
            "scene": 1,  # 场景
            "is_finish": request.data.get('is_finish', False),  # 是否结束
            "duration": 0,  # 时长
            "start_time": cur_time,
            "finish_time": cur_time,
        }
        create_or_update_operate(user, lesson, dict_param, operate_data)
        return Response(rsp_msg_200(result), status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        now_time = datetime.datetime.now()
        # get classroom_id
        try:
            classroom_id = int(kwargs.get('pk', 0))
        except Exception as e:
            logger.error(e)
            return Response(rsp_msg_400(msg='传入的课堂id有误'), status=status.HTTP_200_OK)
        # get object
        if classroom_id == 0:
            instance = get_cur_classroom(user, now_time)
        else:
            instance = self.get_object()
        # 关闭以前异常导致的没有正常关闭的课堂
        try:
            default_class = UserKlassRelationship.objects.get(user=user, is_effect=True, is_default=True).klass
        except Exception as e:
            logger.error(e)
        else:
            close_except_classroom(default_class, user, now_time, instance)
        # return
        if instance is None:
            return Response(rsp_msg_400(msg='没有正在进行的课堂'), status=status.HTTP_200_OK)
        else:
            # 取课程最新数据 (上边对数据进行了更新)
            if classroom_id != 0:
                instance = self.get_object()
            serializer = self.get_serializer(instance)
        return Response(rsp_msg_200(serializer.data))

    @list_route(methods=['GET'])
    def get_classroom_id(self, request):
        """
        暂时不会使用
        :param request:
        
        :return:

            {
              "data": {
                "id": 1177,
                "order": 0,
                "is_active": true,
                "description": null,
                "create_time": "2019-02-19T10:24:06.449422",
                "update_time": "2019-02-19T10:33:52.535641",
                "title": "",
                "start_time": "2019-02-19T10:23:00",
                "finish_time": "2019-02-19T11:03:00",
                "record_date": "2019-02-19",
                "identity": 1,
                "real_finish_time": "2019-02-19T10:24:06.448837",
                "delay_status": 0,
                "effect_time": 0,
                "is_prepare": false,
                "is_open": true,
                "opener": 5,
                "klass": 1,
                "latest_lesson": 58,
                "latest_act": 173,
                "lesson": [
                  42,
                  58,
                  66
                ],
                "server_time": 2019-02-19T10:24:06.448837
              },
              "message": "success",
              "code": 200
            }
        """
        user = request.user
        classroom = get_cur_classroom(user)
        if classroom is None:
            return Response(rsp_msg_400(msg='没有正在进行的课堂'), status=status.HTTP_200_OK)
        serializer = self.get_serializer(classroom)
        result = serializer.data
        # 返回服务器时间 pc端获取不到
        result.update({'server_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def detection_classroom_status(self, request):
        """
        检测当前时间大于下课时间，且没有关闭的课堂 设为无效  \n
        返回正在进行的课堂信息

        :param request:

            {"klass_id": 3}                           用户信息中的班级id
        :return:
        """
        user = request.user
        klass_id = request.query_params.get('klass_id')
        Classroom.objects.filter(opener=user, klass_id=klass_id,
                                 is_open=True, finish_time__lt=datetime.datetime.now()).update(is_active=False)
        try:
            classroom = Classroom.objects.get(opener=user, klass_id=klass_id, finish_time__gt=datetime.datetime.now())
        except:
            return Response(rsp_msg_200(), status=status.HTTP_200_OK)
        else:
            result = ClassroomSerializer(classroom).data
            return Response(rsp_msg_200(result), status=status.HTTP_200_OK)


class ActivityReportViewSet(viewsets.ModelViewSet):
    queryset = ActivityReport.objects.all()
    serializer_class = ActivityReportSerializer
    filter_fields = ('id', 'unit', 'lesson', 'activity', 'classroom', 'user')


class ActivityDetailReportViewSet(viewsets.ModelViewSet):
    queryset = ActivityDetailReport.objects.all()
    serializer_class = ActivityDetailReportSerializer

    @list_route()
    def study_detail_abstractpage(self, request):

        """
        学情统计首页信息 \n
        :param request: \n
            {
                "classroom_id": 1   不传显示最近一堂课内容
                "klass_id": 1
            }

        :return: \n

        """
        user = request.user
        classroom_id = request.GET.get('classrm_id', None)
        klass_id = request.GET.get('klass_id', None)
        if classroom_id is None:
            classroom = Classroom.objects.filter(opener=user, klass_id=klass_id).order_by('-finish_time').first()
        else:
            try:
                classroom = Classroom.objects.get(id=classroom_id)
            except:
                return Response(rsp_msg_400('请传入正确的课堂id'), status=status.HTTP_200_OK)
        operation_record = OperationRecord.objects.filter(classroom=classroom, operation=1).order_by('-finish_time')
        result_list = []
        for act_operation in operation_record:
            try:
                activity = Activity.objects.get(id=act_operation.id)
            except:
                return Response(rsp_msg_400('活动id有误'), status=status.HTTP_200_OK)
            act_data = {'activity_id': activity.id, 'activity_name': activity.title, 'duration': act_operation.duration,
                        'finish_num': act_operation.finish_num, 'has_score': act_operation.has_score,
                        'avg_score': act_operation.avg_score,
                        'student_num': act_operation.finish_num + act_operation.unfinished_num}
            result_list.append(act_data)
        result = {'act_data': result_list, 'classroom_start_time': classroom.start_time,
                  'classroom_finish_time': classroom.finish_time}
        return Response(rsp_msg_200(msg=result), status=status.HTTP_200_OK)

        # 上线前没用到就删除

        # result = []
        # act_queryset = Activity.objects.filter(id=classroom.latest_act)
        # for act in act_queryset:
        #     # 课堂知识巩固数据
        #     steady_act_data = {}
        #
        #     act_finish_people_num = 0
        #     act_type_name_list = {}
        #     score_sum = 0
        #     answer_num = 0
        #     # 活动名称
        #     act_type_name = act.title
        #     act_type_name_list['act_id'] = act.id
        #     act_type_name_list['act_type_name'] = act_type_name
        #     steady_act_data['act_type_name'] = '课堂知识巩固'
        #     student_queryset = UserKlassRelationship.objects.filter(klass=classroom.klass)
        #     # 班级总人数
        #     student_num = student_queryset.count()
        #     act_type_name_list['student_num'] = student_num
        #     steady_act_data['student_num'] = student_num
        #     for index, student in enumerate(student_queryset):
        #         # 练习活动平均成绩
        #         if act.act_type.first_type == 1:
        #             student_info_queryset = ActivityReport.objects.filter(user=student.user, classroom=classroom,
        #                                                                   activity_id=act.id).order_by('add_time')
        #             if student_info_queryset.exists():
        #                 for student_info in student_info_queryset:
        #                     # 记录完成人数
        #                     if student_info.is_complete:
        #                         act_finish_people_num += 1
        #                         break
        #             student_question_queryset = ActivityReport.objects.filter(activity_id=act.id, classroom=classroom,
        #                                                                       user=student.user, answer_max__gt=0)
        #             for question_info in student_question_queryset:
        #                 if question_info.is_complete:
        #                     score_sum += int(question_info.score)
        #                     answer_num += 1
        #         # 学习活动
        #         elif act.act_type.first_type == 2:
        #             act_progress_info = ActivityReport.objects.filter(classroom=classroom, user=student.user,
        #                                                               activity=act.id).first()
        #             if act_progress_info:
        #                 if act_progress_info.progress == 100:
        #                     act_finish_people_num += 1
        #
        #     # 不是学习活动
        #     if act.act_type.first_type == 1:
        #         act_type_name_list['avg_score'] = -1
        #     else:
        #         if answer_num == 0:
        #             act_type_name_list['avg_score'] = 0
        #         else:
        #             act_type_name_list['avg_score'] = round(score_sum / answer_num)
        #     act_type_name_list['act_finish_student_num'] = act_finish_people_num
        #     result.append(act_type_name_list)
        #     # 添加课堂知识巩固
        # return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route(methods=['POST', 'GET'])
    def nearest_class(self, request):
        """
        最近课程学情列表
        :param request: \n
        :return:  \n
        """
        klass_id = request.data.get('klass_id', '')
        classroom_queryser = Classroom.objects.filter(klass_id=klass_id).order_by('-create_time')[:4]
        result = []
        for classroom in classroom_queryser:
            data = {'classroom_id': classroom.id, 'crate_time': classroom.create_time}
            result.append(data)
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)


def get_cur_classroom(user, now_time):
    try:
        default_class = UserKlassRelationship.objects.get(user=user, is_effect=True, is_default=True).klass
    except Exception as e:
        logger.error(e)
        raise BFValidationError("获取默认班级失败")
    finish_time = now_time - datetime.timedelta(minutes=10)
    cur_classroom = Classroom.objects.filter(klass=default_class, opener=user, is_active=True,
                                             finish_time__gte=finish_time, is_open=True).order_by('-create_time')
    if cur_classroom.exists():
        return cur_classroom.first()
    else:
        return None


def close_except_classroom(klass_id, user, now_time, classroom):
    # 将出现异常的没有关闭的课程进行关闭
    finish_time = now_time - datetime.timedelta(minutes=10)
    if classroom:
        if finish_time > classroom.finish_time:
            queryset = Classroom.objects.filter(klass=klass_id, opener=user, is_active=True, is_open=True,
                                                finish_time__lt=finish_time)
        else:
            queryset = Classroom.objects.filter(klass=klass_id, opener=user, is_active=True, is_open=True,
                                              finish_time__lt=finish_time).exclude(id=classroom.id)
    else:
        queryset = Classroom.objects.filter(klass=klass_id, opener=user, is_active=True, is_open=True,
                                            finish_time__lt=finish_time)
    for obj in queryset:
        data = {"effect_time": int((now_time - obj.start_time).total_seconds() * 1000),
                "is_open": False, "real_finish_time": now_time}
        Classroom.objects.update_or_create(defaults=data, **{"id": obj.id})

