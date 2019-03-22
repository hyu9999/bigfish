import copy
import json
import logging

import requests
from django.db import transaction

from bigfish.apps.bfwechat.models import WxUserRelationship
from bigfish.apps.questions.models import Question
from bigfish.apps.textbooks.models import Activity
from bigfish.apps.textbooks.serializers import ActivitySerializer
from bigfish.apps.users.models import BigfishUser
from django.db.models.functions import Coalesce


from bigfish.apps.schools.models import Klass

from django.db.models import Avg, Max, Min, Value, Count
from rest_framework.generics import GenericAPIView
from bigfish.base import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import list_route

from bigfish.apps.homework.models import Homework, PushRecord, ReceiveRecord
from bigfish.apps.homework.serializers import HomeWorkSerializers, PushRecordSerializers
from bigfish.settings.base import WEHOST

from bigfish.utils.check_environment import check_wechat_env
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400

logger = logging.getLogger("django")


class HomeWorkView(viewsets.ModelViewSet):

    queryset = Homework.objects.all()
    serializer_class = HomeWorkSerializers

    @list_route(methods=['GET'])
    def get_homework_act(self, request):
        """
        布置作业
        :param request:cast lesson：课程id , act_belong:判断所属模块 1投屏、2控制\n
        :return:
        """
        lesson = request.GET.get('lesson')
        act_belong = request.GET.get('act_belong')
        if not lesson:
            return Response({'detail': '请传入课程id！', 'code': 400}, status=status.HTTP_200_OK)
        # 根据不同模式取出套用练习
        if act_belong == '1':
            question_queryset = Activity.objects.touping().filter(lesson=lesson, is_active=True, data_type=4)
            results = filtrate_question(question_queryset, act_belong=act_belong)
            return Response(rsp_msg_200(results), status=status.HTTP_200_OK)
        elif act_belong == '2':
            question_queryset = Activity.objects.control().filter(lesson=lesson, is_active=True, pointer='student_test')
            results = filtrate_question(question_queryset, act_belong=act_belong)
            return Response(rsp_msg_200(results), status=status.HTTP_200_OK)
        else:
            detail = 'act_belong参数错误，必须为1或2'
            return Response(rsp_msg_400(msg=detail), status=status.HTTP_200_OK)


class PushRecordView(viewsets.ModelViewSet):

    queryset = PushRecord.objects.all()
    serializer_class = PushRecordSerializers

    @list_route(methods=['POST'])
    def create_task_and_push(self, request):
        """
        投屏 发布作业\n
        {
            "klass": 1,
            "question_data": [{}],
        }
        """
        user = request.user
        klass_id = request.data.get('klass', None)
        errors = []
        if not klass_id:
            errors.append({"message": "班级id为必须传入字段！"})
            return Response(rsp_msg_400(errors), status=status.HTTP_200_OK)
        try:
            Klass.objects.get(id=klass_id)
        except:
            return Response(rsp_msg_400('该班级不存在'))
        question_data = request.data.get('question_data', {})
        a_list = []
        for q in question_data:
            a_id = q['activityId']
            try:
                a_list.index(a_id)
            except:
                a_list.append(a_id)
            else:
                continue
        activity_data = a_list
        data_parmas = {
            'user_id': user.id,
            'question_data': question_data,
            'activity_data': activity_data,
        }
        task_obj = Homework.objects.create(**data_parmas)
        # queryset = UserProfile.objects.filter(default_cid=klass_id, identity="学生")
        queryset = Klass.objects.get(id=klass_id).person.filter(identity="学生")
        if queryset.count() == 0:
            return Response(rsp_msg_200({'user_list': []}), status=status.HTTP_200_OK)
        user_list = queryset.values_list('user__id', flat=True)
        # 创建
        with transaction.atomic():
            tpr = PushRecord.objects.create(
                **{'push_user': user, 'task': task_obj, 'is_active': True, 'klass': klass_id})
            sql_list = []
            for user_id in user_list:
                data_dict = {'task_push_record': tpr, 'user_id': user_id}
                sql = ReceiveRecord(**data_dict)
                sql_list.append(sql)
            ReceiveRecord.objects.bulk_create(sql_list)
            # 推送
            task_obj.push_num = task_obj.push_num + 1
            task_obj.save()
        push_info_to_wx(user_list, task_obj.question_data.__len__())
        return Response(rsp_msg_200({'user_list': user_list}), status=status.HTTP_200_OK)


def push_info_to_wx(user_list, nums):
    """
    推送信息到微信
    :param user_list:
    :param nums:
    :return:
    """
    url = WEHOST + "/api/bfwechat/template_msg_record/send_template/"
    for ul in user_list:
        wx_ul = WxUserRelationship.objects.filter(student=ul)
        if wx_ul.count() == 0:
            continue
        for wxu in wx_ul:
            nick_name = wxu.wx_user.nickname
            student_name = wxu.student.profile.realname
            openid = wxu.wx_user.openid
            first = "Hi~尊敬的{}用户您好！今日（{}）作业已发布请各位家长及时监督学生完成作业。". \
                format(nick_name, wxu.student.profile.realname)
            content = "本次练习总计{}道题目。".format(nums)
            data_temp = {
                "openid": openid,
                "template": {
                    "template_id": "BaEPWB9SVLUYueXexR0ur-ct6IKkP6GIg4WWTvVPRRM",
                    "url": "",
                    "mini_program":
                        {
                            "appid": "wxe083dfd04f3ba126",
                            "pagepath": ""
                        },
                    "data":
                        {
                            "first": {
                                "value": first
                            },
                            "name": {
                                "value": student_name
                            },
                            "subject": {
                                "value": "英语"
                            },
                            "content": {
                                "value": content
                            },
                            "remark": {
                                "value": "点击查看详情"
                            }
                        }
                }
            }
            fmt_url_post(url, **data_temp)
    return


def fmt_url_post(url, **param_dict):
    json_data = json.dumps(param_dict)
    # .encode('utf8')
    # req = Request(method="POST", url=url, data=json_data, headers={'Content-Type': 'application/json'})
    # res = urlopen(req)
    headers = {'Content-Type': 'application/json'}
    response_data = requests.post(url, data=json_data, headers=headers).text
    return response_data


def filtrate_question(question_queryset, act_belong):
    """
    去除套用练习和画图，拖拽题
    """
    if act_belong == '1':
        for question_info in question_queryset:
            question_list = question_info.question_data['question']
            question_id_list = copy.deepcopy(question_list)
            for question_id in question_list:
                try:
                    question = Question.objects.get(id=question_id)
                except:
                    continue
                # 套用练习、涂色题、拖拽题进行筛选
                if question.question_type == '2' and question.show_type == '类型二':
                    question_id_list.remove(question_id)
                elif question.question_type == '4' or question.question_type == '5':
                    question_id_list.remove(question_id)
            question_info.question_data['question'] = question_id_list
        results = ActivitySerializer(question_queryset, many=True).data
        return results
    elif act_belong == '2':
        for question_info in question_queryset:
            question_list = question_info.question_ids.split(',')
            question_id_list = copy.deepcopy(question_list)
            for question_id in question_list:
                try:
                    question = Question.objects.get(id=question_id)
                except:
                    continue
                # 套用练习、涂色题、拖拽题进行筛选
                if question.question_type == '2' and question.show_type == '类型二':
                    question_id_list.remove(question_id)
                elif question.question_type == '4' or question.question_type == '5':
                    question_id_list.remove(question_id)
            question_info.question_ids = ','.join([str(id) for id in question_id_list])
        results = ActivitySerializer(question_queryset, many=True).data
        return results




# class TaskRemindView(GenericAPIView):
#     """
#     作业提醒(获取最新一次推送任务)
#
#     发布并完成次数=0：
#         2.1 教师端发布新作业时，小程序接收到作业提醒并在首页展示，点击作业提醒进入做题界面；
#         2.2 作业提醒包含的信息：图标icon、标题、作业编号、发布时间
#         2.3 表现形式
#             A方案：将成绩榜单顶下去，在榜单上方显示，如图1：
#             B方案：作业提醒不挤占榜单位置，以气泡的形式浮在页面上
#     发布并完成次数>=1
#         2.4 小程序首页显示作业提醒，点击进入做题界面；
#         2.5 作业提醒包含的信息：图标icon、标题、作业编号、分数、发布时间；\n
#
#     :param request:
#
#         user_id=xxx&klass=1
#
#     :return:
#
#         {
#             "data": {
#                 "id":1,
#                 "name": "作业编号1",
#                 "push_time": "2018-11-02T15:26:56",
#                 "user_task_id":1,
#                 "is_complete": True,
#                 "score": 22.0,
#                 "finish_time": "2018-11-02T15:44:25"
#             },
#             "code": 200,
#             "message": "success"
#         }
#     """
#     permission_classes = (AllowAny,)
#     queryset = UserTask.objects.all()
#     serializer_class = UserTaskSerializer
#
#     @check_wechat_env
#     def get(self, request):
#         params = request.query_params
#         tpr = TaskPushRecord.objects.filter(klass=params.get('klass')).order_by('-push_time')
#         if not tpr.exists():
#             raise BFValidationError("暂无作业信息！")
#         data = {"id": tpr.first().id, "name": "作业编号{}".format(tpr.first().id), "push_time": tpr.first().push_time}
#         ut_list = UserTask.objects.filter(task_push_record=tpr.first().id, user_id=params.get('user_id')).order_by(
#             '-create_time')
#         ut_info = UserTaskAppletRemindSerializer(ut_list.first()).data
#         data.update(ut_info)
#         return Response(rsp_msg_200(data), status=status.HTTP_200_OK)
#
#
# class RankListView(GenericAPIView):
#     """
#     成绩排行榜(获取最近一次有数据的推送任务)
#
#     3.1 排名范围：同一个班级内进行最高成绩排名，只显示前3名；
#     3.2 包含信息：名次、头像（系统头像/微信头像）、最高成绩显示、累计完成次数；
#     3.3 排名规则：
#         a.按最高成绩由高到低显示前3名；
#         b.成绩相同时再按照时间排序，最先取得成绩则优先上榜；
#         c.成绩和时间都相同时最后按照上榜频率排序，上榜频率较低的则优先上榜；
#     :param request:
#
#         klass=1
#
#     :return:\n
#         {
#             "message": "success",
#             "data": {
#                 "id": 1,
#                 "data": [
#                     {
#                         "max_score": 75.0,
#                         "user_icon": "",
#                         "realname": "北京学生02",
#                         "user_id": 2312,
#                         "total_times": 2
#                     },
#                     {
#                         "max_score": 75.0,
#                         "user_icon": "",
#                         "realname": "北京学生04",
#                         "user_id": 2314,
#                         "total_times": 1
#                     },
#                     {
#                         "max_score": 66.0,
#                         "user_icon": "",
#                         "realname": "北京学生05",
#                         "user_id": 2315,
#                         "total_times": 2
#                     }
#                 ],
#                 "push_time": "2018-11-06T17:16:29.149294",
#                 "name": "作业编号1"
#             },
#             "code": 200
#         }
#     """
#     permission_classes = (AllowAny,)
#     queryset = TaskPushRecord.objects.all()
#     serializer_class = TaskPushRecordSerializer
#
#     @check_wechat_env
#     def get(self, request):
#         params = request.query_params
#         tpr_list = TaskPushRecord.objects.filter(klass=params.get('klass')).order_by('-push_time')
#         if not tpr_list.exists():
#             raise BFValidationError("暂无作业信息！")
#         ret_data = None
#         for tpr in tpr_list:
#             utr = UserTaskRecord.objects.filter(task_push_record=tpr.id, is_finish=True)
#             if not utr:
#                 continue
#             tmp_dict = UserTaskRecord.objects.filter(
#                 task_push_record=tpr.id, is_finish=True).values('user_id').annotate(
#                 max_score=Max('scores'), total_times=Count('user_id')).order_by('-max_score').values(
#                 'user_id', 'max_score', 'total_times')[0:3]
#             for item in tmp_dict:
#                 try:
#                     user_profile = UserProfile.objects.get(user_id=item.get('user_id'))
#                 except Exception as e:
#                     item['user_icon'] = ''
#                     item['realname'] = ''
#                 else:
#                     item['user_icon'] = user_profile.icon
#                     item['realname'] = user_profile.realname
#
#             ret_data = {"id": tpr.id, "name": "作业编号{}".format(tpr.id), "push_time": tpr.push_time, "data": tmp_dict}
#             break
#         return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
#
#
# class ScoreOverallView(GenericAPIView):
#     """
#     成绩统计数据表(总体情况)
#
#     4.1 数据来源：统计老师发布的最近七个作业，XX学生针对每一个作业的平均成绩、最高成绩、最低成绩
#     4.2 图表表现形式：
#         a.横坐标显示七次作业的发布日期，形式 月-日（xx-xx，例如10-31）
#         b.纵坐标显示成绩0~100分；
#         c.柱状图表示平均成绩，两条折线图表示最高成绩和最低成绩；
#     :param request:\n
#         user_id=xxx&klass=1
#     :return:\n
#         {
#             "data": [
#                 {
#                     "push_id": 6,
#                     "title": "作业6",
#                     "max_score": 56.0,
#                     "min_score": 34.0,
#                     "avg_score": 48.0,
#                     "push_time": "11-02",
#                     "finish_num": 3
#                 },
#                 {
#                     "push_id": 2,
#                     "title": "作业2",
#                     "max_score": 56.0,
#                     "min_score": 53.0,
#                     "avg_score": 54.5,
#                     "push_time": "11-02",
#                     "finish_num": 2
#                 }
#             ],
#             "message": "success",
#             "code": 200
#         }
#     """
#     permission_classes = (AllowAny,)
#     queryset = TaskPushRecord.objects.all()
#     serializer_class = TaskPushRecordSerializer
#
#     @check_wechat_env
#     def get(self, request):
#         tpr = TaskPushRecord.objects.filter(klass=request.query_params.get("klass")).order_by('-push_time')[0:7]
#         ret_data = []
#         for item in tpr:
#             queryset = UserTaskRecord.objects.filter(
#                 task_push_record=item.id, user_id=request.query_params.get("user_id"), is_finish=True
#             ).order_by("-finish_time")
#             if not queryset.exists():
#                 continue
#             ut = queryset.aggregate(avg_score=Avg('scores'), max_score=Max('scores'), min_score=Min('scores'))
#             tmp_dict = {}
#             for k, v in dict(ut).items():
#                 tmp_dict[k] = round(v, 2)
#             tmp_dict["push_id"] = item.id
#             tmp_dict["push_time"] = item.push_time.strftime("%m-%d")
#             tmp_dict["title"] = "作业{}".format(item.id)
#             tmp_dict["finish_num"] = queryset.count()
#             ret_data.append(tmp_dict)
#         ret_data.reverse()
#         return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
#
#
# class ScoreDetailView(GenericAPIView):
#     """
#     成绩统计数据表(详情)
#
#     4.3 点击详情进入子页面，按照时间倒序以折线图的形式展示每个作业的完成情况
#         a.横坐标显示针对第X个作业，学生做题次数
#         a1.次数<=6次，x轴自适应；次数>=6次，x轴显示时间最近6次，例如做了7次，则x轴命名为NO2、NO3、NO4、NO5、N06、NO7,折线图右下角显示“累计完成XX次”
#         b.折线显示每次成绩变化，横线表示累计完成XX次的平均成绩；
#     :param request:\n
#         user_id=2&klass=1&count_num=7
#     :return:\n
#         {
#             "message": "success",
#             "code": 200,
#             "data": {
#                 "data": [
#                     {
#                         "id": 6,
#                         "scores": 34.0,
#                         "finish_time": "2018-11-02T18:16:41"
#                     },
#                     {
#                         "id": 8,
#                         "scores": 56.0,
#                         "finish_time": "2018-11-02T18:43:40"
#                     },
#                     {
#                         "id": 9,
#                         "scores": 54.0,
#                         "finish_time": "2018-11-02T18:46:28"
#                     }
#                 ],
#                 "avg_score": 48.0,
#                 "finish_num": 3
#             }
#         }
#     """
#     permission_classes = (AllowAny,)
#     queryset = UserTaskRecord.objects.all()
#     serializer_class = UserTaskRecordScoreSerializer
#
#     @check_wechat_env
#     def get(self, request):
#         klass = request.GET.get("klass", None)
#         user_id = request.GET.get("user_id", None)
#         try:
#             count_num = int(request.GET.get("count_num"))
#         except Exception as e:
#             logger.error(e)
#             count_num = 7
#         tpr_list = TaskPushRecord.objects.filter(klass=klass).order_by('-push_time')[
#                    0:count_num]
#         ret_data = []
#         for tpr in tpr_list:
#             queryset = self.get_queryset().filter(
#                 is_finish=True, task_push_record=tpr.id, user_id=user_id
#             ).order_by("-finish_time")
#             finish_num = queryset.count()
#             avg_score = queryset.aggregate(data=Coalesce(Avg('scores'), Value(0))).get('data')
#             data = self.get_serializer(queryset[:6], many=True).data
#             data.reverse()
#             tmp_data = {"id": tpr.id, "finish_num": finish_num, "avg_score": round(avg_score, 2),
#                         "push_time": tpr.push_time, "data": data}
#             ret_data.append(tmp_data)
#         return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
#
#
# class TaskDetailView(GenericAPIView):
#     """
#     作业模块功能
#
#     1、作业列表表现形式：时间轴+列表，时间轴按月份划分；
#     1.1 优先显示当前年级下的作业列表，按照时间倒序排列，最新的日期显示在最上方；
#     1.2 点击左上角可选择以往年级，选中之后主页面显示选中年级的作业列表，按照时间倒序排列展开，最新的日期显示在最上方；
#     1.3 点击作业卡片，进入做题页面；
#     1.4 交互规则
#         a.默认情况下，列表展开，完成次数>=1和完成次数=0的作业要有颜色区别；
#         b.点击时间轴上的月份，则收起选中月份包含的作业卡片，再点击一次则展开；
#             b1.若当前月份中所有作业完成次数都>=1，卡片收起最上层封面显示最新日期的作业卡；
#             b2.若当前月份中存在作业完成次数<1，卡片收起最上层封面显示日期最新的未完成作业卡片；
#     :param request:\n
#         {   "user_id": 2,
#             "task_push_record__push_time__date__range": ["2018-11-01", "2018-11-02"]
#         }
#     :return:\n
#         {
#             "message": "success",
#             "code": 200,
#             "data": [
#                 {
#                     "id": 10,
#                     "user_id": 2,
#                     "push_id": 8,
#                     "push_time": "2018-11-02T17:39:15",
#                     "question_num": 2,
#                     "avg_score": null,
#                     "total_times": 31,
#                     "is_read": false
#                 },
#                 {
#                     "id": 7,
#                     "user_id": 2,
#                     "push_id": 5,
#                     "push_time": "2018-11-02T17:38:54",
#                     "question_num": 2,
#                     "avg_score": null,
#                     "total_times": 4,
#                     "is_read": false
#                 },
#                 {
#                     "id": 9,
#                     "user_id": 2,
#                     "push_id": 7,
#                     "push_time": "2018-11-02T17:39:08",
#                     "question_num": 2,
#                     "avg_score": null,
#                     "total_times": 5,
#                     "is_read": true
#                 },
#                 {
#                     "id": 8,
#                     "user_id": 2,
#                     "push_id": 6,
#                     "push_time": "2018-11-02T17:39:01",
#                     "question_num": 2,
#                     "avg_score": 48.0,
#                     "total_times": 1,
#                     "is_read": true
#                 }
#             ]
#         }
#     """
#     permission_classes = (AllowAny,)
#     queryset = UserTask.objects.all().order_by('is_read', '-task_push_record__push_time')
#     serializer_class = UserTaskAppletDetailSerializer
#
#     @check_wechat_env
#     def post(self, request):
#         queryset = self.get_queryset().filter(**request.data)
#         ret_data = self.get_serializer(queryset, many=True).data
#         return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
#
#
# class FormatTermView(GenericAPIView):
#     """
#     根据学校年级获取学期
#
#     :param request: \n
#         school_id=1&grade=小学一年级
#     :return:\n
#         {
#             "message": "success",
#             "data": [
#                 {
#                     "id": 1,
#                     "term_id": 1,
#                     "academic_year": "2018",
#                     "schools": 73,
#                     "start_date": "2018-09-01",
#                     "finish_date": "2019-01-20",
#                     "title": "2018下学年"
#                 },
#                 {
#                     "id": 2,
#                     "term_id": 2,
#                     "academic_year": "2018",
#                     "schools": 73,
#                     "start_date": "2018-02-27",
#                     "finish_date": "2018-09-01",
#                     "title": "2018上学年"
#                 }
#             ],
#             "code": 200
#         }
#     """
#     permission_classes = (AllowAny,)
#     queryset = TermSchedule.objects.all().order_by('order')
#     serializer_class = TermScheduleFmtSerializer
#
#     @staticmethod
#     def get_fmt_term_data(query_data, grade_num):
#         """
#         将学期和年级拼接成有序字符串
#
#         :param query_data:
#         :param grade_num:
#         :return:
#         """
#         ret_data = []
#         for index, item in enumerate(query_data):
#             try:
#                 term = Term.objects.get(id=item.get("term_id")).term
#             except Exception as e:
#                 logger.error(e)
#                 continue
#             else:
#                 term = "上学年" if term == 1 else "下学年"
#             if grade_num > 0:
#                 item['title'] = "{}{}".format(item['academic_year'], term)
#                 ret_data.append(item)
#             if term == "上学年":
#                 grade_num = grade_num - 1
#         return ret_data
#
#     def get(self, request):
#         grade = request.GET.get('grade')
#         school_id = request.GET.get('school_id')
#         queryset = self.get_queryset().filter(is_active=True, school_id=school_id).order_by('-start_date')
#         try:
#             grade_num = [x[1] for x in Klass.GRADE_ORDER if x[0] == grade][0]
#         except Exception as e:
#             raise BFValidationError("未获取到数据")
#         # 处理未配置最新学期产生的异常问题
#         # cur_date = datetime.datetime.now().date()
#         # if not (cur_date > queryset.first().start_date and cur_date < queryset.first().finish_date):
#         #     raise BFValidationError("查询异常！")
#         serializer = TermScheduleFmtSerializer(queryset, many=True)
#         ret_data = self.get_fmt_term_data(serializer.data, grade_num)
#         return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
