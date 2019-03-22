import datetime
import logging

from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.research.models import PrepareLesson, PrepareLessonReply, PrepareLessonWatch, TeachingLog, \
    TeachingLogReply, TeachingLogWatch, ResearchActivity, ResearchActivityReply, ResearchActivityWatch, TeacherSchedule
from bigfish.apps.research.serializers import PrepareLessonSerializer, PrepareLessonReplySerializer, \
    PrepareLessonWatchSerializer, TeachingLogSerializer, TeachingLogReplySerializer, TeachingLogWatchSerializer, \
    ResearchActivitySerializer, ResearchActivityReplySerializer, ResearchActivityWatchSerializer, \
    TeacherScheduleSerializer, SchoolWeekSerializer
from bigfish.apps.schools.models import Klass, School
from bigfish.apps.schools.models import SchoolWeek, Term
from bigfish.apps.users.models import BigfishUser
from bigfish.base import viewsets, status
from bigfish.base.ret_msg import rsp_msg_200
from bigfish.utils.paginations import StandardResultsSetPagination, common_paging

logger = logging.getLogger('django')


class PrepareLessonViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a PrepareLesson instance.
    list:
        Return all PrepareLesson, ordered by most recently joined.
    create:
        Create a new PrepareLesson.
    delete:
        Remove an existing PrepareLesson.
    partial_update:
        Update one or more fields on an existing PrepareLesson.
    update:
        Update a PrepareLesson.
    """
    queryset = PrepareLesson.objects.all()
    serializer_class = PrepareLessonSerializer
    pagination_class = StandardResultsSetPagination
    filter_fields = ('title', 'teacher_schedule__klass', 'teacher_schedule__teacher',)

    @list_route(methods=['GET'])
    def get_pl_list(self, request):
        pl_id = request.GET.get("pl_id")
        title = request.GET.get('title')
        if pl_id:
            pl_list = PrepareLesson.objects.filter(id=pl_id, is_active=True).order_by('-create_time')
        else:
            if title:
                pl_list = PrepareLesson.objects.filter(title__icontains=title, is_active=True).order_by('-create_time')
            else:
                pl_list = PrepareLesson.objects.filter(is_active=True).order_by('-create_time')
        data = get_list_data(pl_list, 1)
        page = common_paging(data, request)
        return Response(rsp_msg_200(extra=page), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_user_post_list(self, request):
        user = request.GET.get("user")
        klass = request.GET.get('klass')
        if user and klass:
            pl_list = PrepareLesson.objects.filter(teacher_schedule__teacher=user, teacher_schedule__klass=klass,
                                                   is_active=True).order_by('-create_time')
            tl_list = TeachingLog.objects.filter(teacher_schedule__teacher=user, teacher_schedule__klass=klass,
                                                 is_active=True).order_by('-create_time')
        elif user:
            pl_list = PrepareLesson.objects.filter(teacher_schedule__teacher=user, is_active=True). \
                order_by('-create_time')
            tl_list = TeachingLog.objects.filter(teacher_schedule__teacher=user, is_active=True). \
                order_by('-create_time')
        elif klass:
            pl_list = PrepareLesson.objects.filter(teacher_schedule__klass=klass, is_active=True). \
                order_by('-create_time')
            tl_list = TeachingLog.objects.filter(teacher_schedule__klass=klass, is_active=True).order_by('-create_time')
        else:
            pl_list = []
            tl_list = []
        data = []
        data_pl = get_list_data(pl_list, 1)
        data_tl = get_list_data(tl_list, 2)
        data.append(data_pl)
        data.append(data_tl)
        page = common_paging(data, request)
        return Response(rsp_msg_200(extra=page), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_ranking_list(self, request):
        list_type = request.GET.get('type', 1)
        user_pro_list = BigfishUser.objects.filter(identity="老师")
        results = []
        for user_pro in user_pro_list:
            data = {}
            if list_type == '1' or list_type == 1:
                data['nums'] = PrepareLesson.objects.filter(teacher_schedule__teacher=user_pro.user, is_active=True). \
                    count()
            elif list_type == '2' or list_type == 2:
                data['nums'] = TeachingLog.objects.filter(teacher_schedule__teacher=user_pro.user, is_active=True). \
                    count()
            data['real_name'] = user_pro.realname
            try:
                klass_obj = Klass.objects.get(id=user_pro.default_cid)
                if klass_obj.school.is_normal:
                    data['school'] = klass_obj.school.name
                else:
                    continue
            except:
                data['school'] = "请设置默认班级ID！"
                continue
            results.append(data)
        results.sort(key=lambda e: e['nums'], reverse=True)
        return Response({"detail": results, "code": 200}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_home_data(self, request):
        n_time = datetime.datetime.now()
        results = []
        pl_obj = PrepareLesson.objects.filter(is_active=True).order_by('-create_time').first()
        data = PrepareLessonSerializer(pl_obj).data
        data['day_nums'] = PrepareLesson.objects.filter(is_active=True,
                                                        create_time__date=datetime.date(n_time.year,
                                                                                        n_time.month,
                                                                                        n_time.day)).count()
        data['total_nums'] = PrepareLesson.objects.filter(is_active=True).count()
        if pl_obj:
            data['name'] = pl_obj.teacher_schedule.teacher.profile.realname
            klass_obj = pl_obj.teacher_schedule.klass
            data['klass_name'] = klass_obj.grade + klass_obj.name
            data['klass_id'] = klass_obj.id
            data['school_name'] = pl_obj.teacher_schedule.description
            data['week_day'] = pl_obj.teacher_schedule.get_week_display()
            data['user_id'] = pl_obj.teacher_schedule.teacher.id
        results.append(data)

        tl_obj = TeachingLog.objects.filter(is_active=True).order_by('-create_time').first()
        data = TeachingLogSerializer(tl_obj).data
        data['day_nums'] = TeachingLog.objects.filter(is_active=True,
                                                      create_time__date=datetime.date(n_time.year,
                                                                                      n_time.month,
                                                                                      n_time.day)).count()
        data['total_nums'] = TeachingLog.objects.filter(is_active=True).count()
        if tl_obj:
            data['name'] = tl_obj.teacher_schedule.teacher.profile.realname
            klass_obj = tl_obj.teacher_schedule.klass
            data['klass_name'] = klass_obj.grade + klass_obj.name
            data['klass_id'] = klass_obj.id
            data['school_name'] = tl_obj.teacher_schedule.description
            data['week_day'] = tl_obj.teacher_schedule.get_week_display()
            data['user_id'] = tl_obj.teacher_schedule.teacher.id
        results.append(data)

        ra_obj = ResearchActivity.objects.filter(is_active=True).order_by('-create_time').first()
        data = ResearchActivitySerializer(ra_obj).data
        data['day_nums'] = ResearchActivity.objects.filter(is_active=True,
                                                           create_time__date=datetime.date(n_time.year,
                                                                                           n_time.month,
                                                                                           n_time.day)).count()
        data['total_nums'] = ResearchActivity.objects.filter(is_active=True).count()
        if ra_obj:
            data['name'] = ra_obj.user.profile.realname
            data['user_id'] = ra_obj.user.id
        results.append(data)
        return Response({"results": results, "code": 200}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_post_nums(self, request):
        user_id = request.GET.get('user')
        results = {}
        pl_nums = PrepareLesson.objects.filter(is_active=True, teacher_schedule__teacher=user_id).count()
        tl_nums = TeachingLog.objects.filter(is_active=True, teacher_schedule__teacher=user_id).count()
        results['pl_nums'] = pl_nums
        results['tl_nums'] = tl_nums
        return Response({"results": results, "code": 200}, status=status.HTTP_200_OK)


class PrepareLessonReplyViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a PrepareLessonReply instance.
    list:
        Return all PrepareLessonReply, ordered by most recently joined.
    create:
        Create a new PrepareLessonReply.
    delete:
        Remove an existing PrepareLessonReply.
    partial_update:
        Update one or more fields on an existing PrepareLessonReply.
    update:
        Update a PrepareLessonReply.
    """
    queryset = PrepareLessonReply.objects.all()
    serializer_class = PrepareLessonReplySerializer
    filter_fields = ('prepare_lesson',)


class PrepareLessonWatchViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a PrepareLessonWatch instance.
    list:
        Return all PrepareLessonWatch, ordered by most recently joined.
    create:
        Create a new PrepareLessonWatch.
    delete:
        Remove an existing PrepareLessonWatch.
    partial_update:
        Update one or more fields on an existing PrepareLessonWatch.
    update:
        Update a PrepareLessonWatch.
    """
    queryset = PrepareLessonWatch.objects.all()
    serializer_class = PrepareLessonWatchSerializer


class TeachingLogViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a TeachingLog instance.
    list:
        Return all TeachingLog, ordered by most recently joined.
    create:
        Create a new TeachingLog.
    delete:
        Remove an existing TeachingLog.
    partial_update:
        Update one or more fields on an existing TeachingLog.
    update:
        Update a TeachingLog.
    """
    queryset = TeachingLog.objects.all()
    serializer_class = TeachingLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_fields = ('title', 'teacher_schedule__klass', 'teacher_schedule__teacher',)

    # @staticmethod
    # def get_online_time(time_range):
    #     """
    #     计算某节课APP在线时长
    #
    #     :param time_range:
    #     :return:
    #     """
    #     task_list = Task.objects.filter(open_date__range=time_range)
    #     course_finish_time = datetime.datetime.strptime(time_range[1], "%Y-%m-%d %H:%M:%S")
    #     all_time = sum(
    #         [(course_finish_time - x.open_date) if x.finish_time > course_finish_time else (x.finish_time - x.open_date)
    #          for x in task_list])
    #     return all_time

    def create(self, request, *args, **kwargs):
        param = request.data.copy()
        progress = param.get("progress")
        # 进度100% 计算在线时长
        if progress == 100:
            teacher_schedule = param.get("teacher_schedule")
            ts = TeacherSchedule.objects.get(id=teacher_schedule)
            time_range = ts.class_schedule.schedule_data[ts.schedule]
            teaching_date = param.get("teaching_date")
            time_range = ["{} {}".format(time_range, x) for x in teaching_date]
            online_time = self.get_online_time(time_range)
            if online_time >= 15:
                mode = 2
            else:
                mode = 1
            param["online_time"] = online_time
            param["mode"] = mode

        serializer = self.get_serializer(data=param)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['GET'])
    def get_tlog_list(self, request):
        tlog_id = request.GET.get("tlog_id")
        title = request.GET.get('title')
        if tlog_id:
            tlog_list = TeachingLog.objects.filter(id=tlog_id, is_active=True).order_by('-create_time')
        else:
            if title:
                tlog_list = TeachingLog.objects.filter(title__icontains=title, is_active=True).order_by('-create_time')
            else:
                tlog_list = TeachingLog.objects.filter(is_active=True).order_by('-create_time')
        data = get_list_data(tlog_list, 2)
        page = common_paging(data, request)
        return Response(rsp_msg_200(extra=page), status=status.HTTP_200_OK)


class TeachingLogReplyViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a TeachingLogReply instance.
    list:
        Return all TeachingLogReply, ordered by most recently joined.
    create:
        Create a new TeachingLogReply.
    delete:
        Remove an existing TeachingLogReply.
    partial_update:
        Update one or more fields on an existing TeachingLogReply.
    update:
        Update a TeachingLogReply.
    """
    queryset = TeachingLogReply.objects.all()
    serializer_class = TeachingLogReplySerializer
    filter_fields = ('teaching_log',)


class TeachingLogWatchViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a TeachingLogWatch instance.
    list:
        Return all TeachingLogWatch, ordered by most recently joined.
    create:
        Create a new TeachingLogWatch.
    delete:
        Remove an existing TeachingLogWatch.
    partial_update:
        Update one or more fields on an existing TeachingLogWatch.
    update:
        Update a TeachingLogWatch.
    """
    queryset = TeachingLogWatch.objects.all()
    serializer_class = TeachingLogWatchSerializer


class ResearchActivityViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a ResearchActivity instance.
    list:
        Return all ResearchActivity, ordered by most recently joined.
    create:
        Create a new ResearchActivity.
    delete:
        Remove an existing ResearchActivity.
    partial_update:
        Update one or more fields on an existing ResearchActivity.
    update:
        Update a ResearchActivity.
    """
    queryset = ResearchActivity.objects.all()
    serializer_class = ResearchActivitySerializer
    pagination_class = StandardResultsSetPagination
    filter_fields = ('title',)

    @list_route(methods=['GET'])
    def get_ra_list(self, request):
        ra_id = request.GET.get("ra_id")
        ra_title = request.GET.get('title')
        if ra_id:
            ra_list = ResearchActivity.objects.filter(id=ra_id, is_active=True).order_by('-create_time')
        else:
            if ra_title:
                ra_list = ResearchActivity.objects.filter(title__icontains=ra_title, is_active=True). \
                    order_by('-create_time')
            else:
                ra_list = ResearchActivity.objects.filter(is_active=True).order_by('-create_time')
        data = []
        for ra in ra_list:
            ra_data = ResearchActivitySerializer(ra).data
            ra_data['name'] = ra.user.profile.realname
            ra_data['reply_nums'] = ResearchActivityReply.objects.filter(research_activity=ra).count()
            last_ra = ResearchActivityReply.objects.filter(research_activity=ra).order_by('-create_time').first()
            if last_ra:
                ra_data['last_reply_name'] = last_ra.user.profile.realname
                ra_data['last_reply_data'] = last_ra.create_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                ra_data['last_reply_name'] = ""
                ra_data['last_reply_data'] = ""
            ra_data['watch_nums'] = ResearchActivityWatch.objects.filter(research_activity=ra).count()
            ra_data['icon'] = ra.user.profile.icon
            data.append(ra_data)
        page = common_paging(data, request)
        return Response(rsp_msg_200(extra=page), status=status.HTTP_200_OK)


class ResearchActivityReplyViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a ResearchActivityReply instance.
    list:
        Return all ResearchActivityReply, ordered by most recently joined.
    create:
        Create a new ResearchActivityReply.
    delete:
        Remove an existing ResearchActivityReply.
    partial_update:
        Update one or more fields on an existing ResearchActivityReply.
    update:
        Update a ResearchActivityReply.
    """
    queryset = ResearchActivityReply.objects.all()
    serializer_class = ResearchActivityReplySerializer
    filter_fields = ('research_activity',)


class ResearchActivityWatchViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a ResearchActivityWatch instance.
    list:
        Return all ResearchActivityWatch, ordered by most recently joined.
    create:
        Create a new ResearchActivityWatch.
    delete:
        Remove an existing ResearchActivityWatch.
    partial_update:
        Update one or more fields on an existing ResearchActivityWatch.
    update:
        Update a ResearchActivityWatch.
    """
    queryset = ResearchActivityWatch.objects.all()
    serializer_class = ResearchActivityWatchSerializer


class TeacherScheduleViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a TeacherSchedule instance.
    list:
        Return all TeacherSchedule, ordered by most recently joined.
    create:
        Create a new TeacherSchedule.
    delete:
        Remove an existing TeacherSchedule.
    partial_update:
        Update one or more fields on an existing TeacherSchedule.
    update:
        Update a TeacherSchedule.
    """
    queryset = TeacherSchedule.objects.all()
    serializer_class = TeacherScheduleSerializer
    filter_fields = ('teacher', 'klass',)

    @list_route(methods=['GET'])
    def teacher_get_info(self, request):
        user = request.GET.get('user')
        try:
            user_obj = BigfishUser.objects.get(user=user)
            klass_list = user_obj.attend_class.all()
        except:
            return Response({"detail": "所传入的用户不存在", "code": 400}, status=status.HTTP_200_OK)
        klass_data = []
        for klass in klass_list:
            temp_kdata = {}
            temp_kdata['id'] = klass.id
            temp_kdata['name'] = klass.grade + klass.name
            klass_data.append(temp_kdata)
            s_list = TeacherSchedule.objects.filter(teacher=user, klass=klass).order_by('week')
            klass_schedule = []
            for s in s_list:
                temp_s = {}
                temp_s['id'] = s.id
                temp_s['name'] = "{}{}".format(s.get_week_display(), s.get_schedule_display())
                klass_schedule.append(temp_s)
            temp_kdata['schedule'] = klass_schedule
        return Response({"detail": klass_data, "code": 200}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_teacher_schedule(self, request):
        user_id = request.GET.get('user')
        if not user_id:
            return Response({"detail": "请传入正确的用户ID！", "code": 400}, status=status.HTTP_200_OK)
        s_list = TeacherSchedule.objects.filter(teacher=user_id).order_by('klass')
        results = []
        for s in s_list:
            try:
                klass_obj = Klass.objects.get(id=s.klass.id)
                s_data = TeacherScheduleSerializer(s).data
                s_data['klass_name'] = klass_obj.grade + klass_obj.name
            except:
                s_data['klass_name'] = "错误的班级ID"
            results.append(s_data)
        return Response({"detail": results, "code": 200}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_school_teachers(self, request):
        school_id = request.GET.get('school', None)
        if not school_id:
            return Response({"detail": "请传入正确的学校ID！", "code": 400}, status=status.HTTP_200_OK)
        try:
            school = School.objects.get(id=school_id)
        except:
            return Response({"detail": "请传入正确的学校ID！", "code": 400}, status=status.HTTP_200_OK)
        results = []
        user_list = BigfishUser.objects.filter(identity="老师")
        for user in user_list:
            if user.school() == school:
                temp = {}
                temp['id'] = user.user_id
                temp['name'] = user.realname
                results.append(temp)
        return Response({"detail": results, "code": 200}, status=status.HTTP_200_OK)


class SchoolWeekViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a SchoolWeek instance.
    list:
        Return all SchoolWeek, ordered by most recently joined.
    create:
        Create a new SchoolWeek.
    delete:
        Remove an existing SchoolWeek.
    partial_update:
        Update one or more fields on an existing SchoolWeek.
    update:
        Update a SchoolWeek.
    """
    queryset = SchoolWeek.objects.all()
    serializer_class = SchoolWeekSerializer


# class TermScheduleViewSet(viewsets.ModelViewSet):
#     """
#     retrieve:
#         Return a TermSchedule instance.
#     list:
#         Return all TermSchedule, ordered by most recently joined.
#     create:
#         Create a new TermSchedule.
#     delete:
#         Remove an existing TermSchedule.
#     partial_update:
#         Update one or more fields on an existing TermSchedule.
#     update:
#         Update a TermSchedule.
#     """
#     queryset = TermSchedule.objects.all()
#     serializer_class = TermScheduleSerializer
#     filter_fields = ('id', 'title', 'term', 'term_id', 'schools', 'school_id', 'is_active', 'start_date', 'finish_date')

    @staticmethod
    def get_fmt_term_data(query_data, grade_num):
        """
        将学期和年级拼接成有序字符串

        :param query_data:
        :param grade_num:
        :return:
        """
        ret_data = []
        for index, item in enumerate(query_data):
            try:
                term = Term.objects.get(id=item.get("term_id")).term
            except Exception as e:
                logger.error(e)
                continue
            else:
                term = "上册" if term == 1 else "下册"
            if grade_num > 0:
                item['title'] = "{}{}".format([x[0] for x in Klass.GRADE_ORDER if x[1] == grade_num][0], term)
                ret_data.append(item)
            if term == "上册":
                grade_num = grade_num - 1
        return ret_data

    # @list_route()
    # def fmt_term_list(self, request, *args, **kwargs):
    #     """
    #     根据学校年级获取学期
    #
    #     :param request: \n
    #         school_id=1&grade=小学一年级
    #     :param args:
    #     :param kwargs:
    #     :return:\n
    #         {
    #             "message": "success",
    #             "code": 200,
    #             "data": {
    #                 "count": 2,
    #                 "next": null,
    #                 "previous": null,
    #                 "results": [
    #                     {
    #                         "id": 1,
    #                         "term_id": 1,
    #                         "schools": 1,
    #                         "start_date": "2018-09-01",
    #                         "finish_date": "2019-02-28",
    #                         "title": "小学二年级上册"
    #                     },
    #                     {
    #                         "id": 3,
    #                         "term_id": 2,
    #                         "schools": 1,
    #                         "start_date": "2018-02-01",
    #                         "finish_date": "2018-08-31",
    #                         "title": "小学一年级下册"
    #                     }
    #                 ]
    #             }
    #         }
    #     """
    #     param = request.query_params.dict()
    #     grade = param.get('grade')
    #     param.pop('grade', None)
    #     queryset = self.get_queryset().filter(is_active=True).filter(**param).order_by('-start_date')
    #     try:
    #         grade_num = [x[1] for x in Klass.GRADE_ORDER if x[0] == grade][0]
    #     except Exception as e:
    #         raise BFValidationError("未获取到数据")
    #     # 处理未配置最新学期产生的异常问题
    #     # cur_date = datetime.datetime.now().date()
    #     # if not (cur_date > queryset.first().start_date and cur_date < queryset.first().finish_date):
    #     #     raise BFValidationError("查询异常！")
    #     serializer = TermScheduleFmtSerializer(queryset, many=True)
    #     ret_data = self.get_fmt_term_data(serializer.data, grade_num)
    #     return Response(ret_data)


def get_list_data(list_data, data_type):
    data = []
    for ld in list_data:
        if data_type == 1:
            temp_data = PrepareLessonSerializer(ld).data
            temp_data['reply_nums'] = PrepareLessonReply.objects.filter(prepare_lesson=ld).count()
            last_data = PrepareLessonReply.objects.filter(prepare_lesson=ld).order_by('-create_time').first()
            temp_data['watch_nums'] = PrepareLessonWatch.objects.filter(prepare_lesson=ld).count()
        else:
            temp_data = TeachingLogSerializer(ld).data
            temp_data['reply_nums'] = TeachingLogReply.objects.filter(teaching_log=ld).count()
            last_data = TeachingLogReply.objects.filter(teaching_log=ld).order_by('-create_time').first()
            temp_data['watch_nums'] = TeachingLogWatch.objects.filter(teaching_log=ld).count()
        temp_data['data_type'] = data_type
        temp_data['name'] = ld.teacher_schedule.teacher.profile.realname
        if last_data:
            temp_data['last_reply_name'] = last_data.user.profile.realname
            temp_data['last_reply_data'] = last_data.create_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            temp_data['last_reply_name'] = ""
            temp_data['last_reply_data'] = ""
        klass_obj = ld.teacher_schedule.klass
        temp_data['klass_name'] = klass_obj.grade + klass_obj.name
        temp_data['klass_id'] = klass_obj.id
        temp_data['school_name'] = ld.teacher_schedule.description
        temp_data['week_day'] = ld.teacher_schedule.get_week_display()
        temp_data['schedule'] = ld.teacher_schedule.schedule
        temp_data['schedule_id'] = ld.teacher_schedule.id
        temp_data['userId'] = ld.teacher_schedule.teacher.id
        temp_data['icon'] = ld.teacher_schedule.teacher.profile.icon
        data.append(temp_data)
    return data
