import datetime
import logging
import xlrd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction
from rest_auth.models import TokenModel
from rest_auth.registration.views import RegisterView
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from bigfish.apps.classrooms.views import get_cur_classroom
from bigfish.apps.resources.models import Image
from bigfish.apps.schools.models import KlassProgress, RegisterSerial, School, Klass
from bigfish.apps.schools.serializers import KlassBaseSerializer, TeacherCourseSerializer
from bigfish.apps.textbooks.models import Lesson, Activity, Unit
from bigfish.apps.textbooks.views import init_klass_act_progress
from bigfish.apps.users.models import UserFeedback, BigfishUser, UserKlassRelationship, UserOnline, UserCourse, \
    UserPosition, UserScenariosReport, BigFishSession, UserReg
from bigfish.apps.users.serializers import AuthUserSerializer, UserSerializer, UserFeedbackSerializer, \
    UserOnlineSerializer, UserCourseSerializer, UserKlassRelationshipSerializer, SNRegisterSerializer, \
    UserPositionSerializer, UserScenariosRopSerializer, BigFishSessionSerializer, UserRegSerializer
from bigfish.base import viewsets, status
from bigfish.base.const import TEACHER
from bigfish.base.permissions import OnlyTeacher
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400
from bigfish.base.viewsets import BulkModelViewSet
from bigfish.utils.functions import generate_num_username
from bigfish.utils.push_jpush import get_json_data, normal_send_message

logger = logging.getLogger('django')


class UserViewSet(viewsets.ModelViewSet):
    """
    用户创建修改删除
    """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.filter(is_superuser=False)
    filter_fields = {
        "id": ["exact"],
        "username": ["exact", "contains"],
        "identity": ["exact"],
        "attend_class__school__title": ["contains"],
        "attend_class__school__id": ["exact"],
        "attend_class__id": ["exact"],
        "realname": ["exact", "contains"],
        "is_active": ["exact"],
    }

    @list_route()
    def get_user_klass(self, request):
        """
        获取用户班级信息  不传值获取当前用户班级
        :param request: \n
            {"user_id": 1}
        :return: \n
        """
        user_id = request.GET.get('user_id', None)
        if user_id is None:
            user_id = request.user.id
        user = BigfishUser.objects.get(id=user_id)
        klass_queryset = user.attend_class.all()
        ret_data = KlassBaseSerializer(klass_queryset, many=True).data
        if not ret_data:
            return Response(rsp_msg_200(data=[]), status=status.HTTP_200_OK)
        for klass_data in ret_data:
            klass_id = klass_data['id']
            try:
                user_klass = UserKlassRelationship.objects.get(user_id=user_id, klass_id=klass_id)
            except:
                return Response(rsp_msg_400("用户配置班级有误"), status=status.HTTP_200_OK)
            klass_data['is_default'] = user_klass.is_default
        # print(ret_data)
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)

    @list_route(methods=["GET"])
    def user_login_status(self, request):
        """
        班级用户登陆详情
        """
        user = request.user
        if user.identity == 2:
            return Response(rsp_msg_400("学生没有权限调用此接口"), status=status.HTTP_200_OK)
        klass_id = request.GET.get('klass_id')
        user_klass_rel_queryset = UserKlassRelationship.objects.filter(klass_id=klass_id, user__identity=2)
        if not user_klass_rel_queryset.exists():
            return Response(rsp_msg_400("班级不存在 或 班级下没有用户"), status=status.HTTP_200_OK)
        login_count = 0
        logout_count = 0
        data_list = []
        for user_klass_rel in user_klass_rel_queryset:
            tmp_dict = {}
            tmp_dict['id'] = user_klass_rel.user.id
            tmp_dict['name'] = user_klass_rel.user.realname
            try:
                tmp_dict['icon'] = user_klass_rel.user.icon.url
            except:
                tmp_dict['icon'] = ''
            # 判断用户在线状态
            try:
                if user_klass_rel.user.online.is_online:
                    login_count += 1
                    tmp_dict['is_active'] = True
                else:
                    logout_count += 1
                    tmp_dict['is_active'] = False
            except:
                logout_count += 1
                tmp_dict['is_active'] = False
            data_list.append(tmp_dict)
        # 将没有上线的排在前边
        data_list = sorted(data_list, key=lambda data_list: data_list['is_active'])
        data = {"max_count": login_count + logout_count, "login": login_count, "logout": logout_count,
                "data_list": data_list}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def user(self, request):
        """
        标记用户
        :param request:

            {
                "user_id": 1,
                "status": 0
            }
        :return:
        """
        user_id = request.data.get('user_id', None)
        status = request.data.get('status', None)
        if not all([user_id, status]):
            return Response(rsp_msg_400('缺少参数'), status=status.HTTP_200_OK)
        UserOnline.objects.filter(user_id=user_id).update(is_mark=True, status=status)
        return Response(rsp_msg_200(), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def change_user_header(self, request):
        """
        更换用户头像

        :param request: \n
            {
                "id":1
            }
        :return:
        """
        user = request.user
        # 检测图片
        try:
            obj = Image.objects.get(id=request.data.get("id", None))
        except Exception as e:
            return Response(rsp_msg_400("图片不存在"), status=status.HTTP_200_OK)
        # 存储头像
        try:
            user.icon = obj.res
        except Exception as e:
            return Response(rsp_msg_400("保存头像失败"), status=status.HTTP_200_OK)
        else:
            user.save()
        # 返回数据
        if obj.res:
            url = obj.res.url
        else:
            url = ""
        data = {"res": url}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def import_user(self, request):
        """
        导入用户信息 \n
        \t导入表头：账号（可为空，自动生成规则——角色（s/t）+学校码后三位+名字缩写+自增编号）/真实姓名/昵称/性别/年级/班级/角色/学校码/
            [省学籍号/国家学籍号、身份证号] \n
        \t参数：  {"file_url":"/media/xxx.xlsx"}

        学生只可指定一个班级
        老师可以指定多个班级
        """

        file_url = request.data.get("file_url", None)
        file_path = settings.MEDIA_ROOT.replace("/media", "") + file_url
        print(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        errors = []
        with transaction.atomic():
            for index in range(1, sheet.nrows):
                values = [str(item.value) for item in sheet.row(index)]
                if not (values[1] and values[3] and values[4] and values[5] and values[6] and values[7]):
                    errors.append({"line": index + 1, "message": "关键信息不能为空"})
                    continue
                if values[0].endswith(".0"):
                    username = values[0][:-2]
                else:
                    username = values[0]
                realname = values[1]
                nickname = values[2]
                sex = values[3]
                if sex == '1':
                    sex = 1
                elif sex == '2':
                    sex = 2
                else:
                    pass
                grade = int(values[4])
                name = values[5]
                identity = int(values[6].split('.')[0])
                try:
                    coding = values[7].split('.')[0]
                    # 学校id
                    # school_id = values[7]
                    school = School.objects.get(coding=coding)
                except:
                    errors.append({"line": index + 1, "message": "学校不存在"})
                    continue
                try:
                    klass = Klass.objects.get(school_id=school.id, grade=grade, title=name)
                except:
                    errors.append({"line": index + 1, "message": "班级不存在"})
                    continue
                province_code = values[8]
                student_code = values[9]
                card_id = values[10]
                if not username:
                    username = generate_num_username(identity, coding)
                data = {
                    "username": username,
                    "password": "123456",
                    "is_staff": True,
                    "realname": realname,
                    "nickname": nickname,
                    "sex": sex,
                    "identity": identity,
                    "province_code": province_code,
                    "student_code": student_code,
                    "card_id": card_id,
                    "reg": {'user': 0},
                    "school": school.id
                }
                try:
                    exist_user = BigfishUser.objects.get(username=data.get('username', None))
                except:
                    # create --user
                    serializer = UserSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    instance = serializer.save()
                    # create --klass
                    if klass:
                        UserKlassRelationship.objects.create(klass=klass, user=instance, is_default=True)
                    else:
                        errors.append({"line": index + 1, "message": "该老师班级已经添加"})
                        continue
                else:
                    # update
                    if data['identity'] == 2:
                        # student jump
                        errors.append({"line": index + 1, "message": "该学生账号已存在"})
                        continue
                    else:
                        # teacher create class
                        if klass in exist_user.attend_class.all():
                            errors.append({"line": index + 1, "message": "该老师班级已经添加"})
                            continue
                        else:
                            UserKlassRelationship.objects.create(klass=klass, user=exist_user)
        if errors:
            if (sheet.nrows - 1) == len(errors):
                return Response(rsp_msg_400('序号错误'), status=status.HTTP_200_OK)
            return Response(rsp_msg_400(errors), status=status.HTTP_200_OK)
        else:
            return Response(rsp_msg_200(), status=status.HTTP_200_OK)


class AuthUserViewSet(viewsets.RetrieveUpdateAPIView):
    """
    用户创建修改删除
    """
    serializer_class = AuthUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        https://github.com/Tivix/django-rest-auth/issues/275
        """
        return get_user_model().objects.none()


class UserRegViewSet(viewsets.ModelViewSet):
    """
    用户注册id
    """
    queryset = UserReg.objects.all()
    serializer_class = UserRegSerializer
    filter_fields = ('user', 'registration_id')


class AuthUserCourseView(GenericAPIView):
    queryset = UserCourse
    serializer_class = UserCourseSerializer

    def get_object(self):
        textbook_id = self.request.data.get('textbook', None)
        unit_id = self.request.data.get('unit', None)
        lesson_id = self.request.data.get('lesson', None)
        if self.request.user.identity == TEACHER:
            try:
                uk = UserKlassRelationship.objects.get(user=self.request.user, is_effect=True, is_default=True)
            except:
                raise BFValidationError('获取用户默认班级错误')
            try:
                instance = KlassProgress.objects.get(klass_id=uk.klass_id)
            except Exception as e:
                if self.request.method == 'GET':
                    return None
                elif self.request.method == 'PATCH':
                    act_total_num = Activity.objects.filter(lesson_id=lesson_id).count()
                    klass_progress_data = {'textbook_id': textbook_id, 'unit_id': unit_id, 'lesson_id': lesson_id,
                                           'act_total_num': act_total_num, 'klass_id': uk.klass_id}
                    instance = KlassProgress.objects.create(**klass_progress_data)
                else:
                    return None
        else:
            try:
                instance = self.request.user.course
            except Exception as e:
                if self.request.method == 'PATCH':
                    user_course_data = {'textbook_id': textbook_id, 'unit_id': unit_id, 'lesson_id': lesson_id,
                                        'user': self.request.user}
                    instance = UserCourse.objects.create(**user_course_data)
                else:
                    return None
        return instance

    def get_queryset(self):
        return UserCourse.objects.none()

    def get(self, request):
        """
        获取当前学习进度

        :return:\n
            {
                "data": {
                    "klass": null,
                    "textbook": null,
                    "unit": null,
                    "lesson": null
                },
                "message": "success",
                "code": 200
            }

        """
        instance = self.get_object()
        if request.user.identity == TEACHER:
            ret_data = TeacherCourseSerializer(instance).data
        else:
            ret_data = self.get_serializer(instance).data
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        更新教材学习进度

        :param request: \n
            {
                "textbook":1,
                "unit":1,
                "lesson":1
            }
        :return:\n
            {
              "data": {
                "klass": 5,
                "textbook": 6,
                "unit": 36,
                "lesson": 7
              },
              "message": "success",
              "code": 200
            }
        """
        user = request.user
        lesson_id = request.data.get('lesson', None)
        instance = self.get_object()
        if request.user.identity == TEACHER:
            serializer = TeacherCourseSerializer(instance, data=request.data, partial=True)
            # 更新课堂中的数据
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except:
                return Response(rsp_msg_400('课程id不存在'), status=status.HTTP_200_OK)
            now_time = datetime.datetime.now()
            classroom = get_cur_classroom(user, now_time)
            # 判断是否在上课
            if classroom is None:
                pass
            else:
                if lesson_id not in list(classroom.lesson.all().values_list('id', flat=True)):
                    classroom.lesson.add(lesson)
                classroom.latest_lesson = lesson
                classroom.save()
            # 初始化班级活动进度
            init_klass_act_progress(lesson_id, instance.klass_id)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(rsp_msg_200(serializer.data), status=status.HTTP_200_OK)


class UserKlassRelationshipViewSet(BulkModelViewSet):
    """
    用户班级关系
    """
    queryset = UserKlassRelationship.objects.all()
    serializer_class = UserKlassRelationshipSerializer
    filter_fields = {
        "id": ["exact"],
        "user": ["exact"],
        "klass": ["exact"],
        "study_progress": ["exact"],
        "is_effect": ["exact"],
        "is_default": ["exact"],
        "update_time": ["exact"],
        "add_time": ["exact"],
    }


class UserOnlineViewSet(viewsets.ModelViewSet):
    queryset = UserOnline.objects.all()
    serializer_class = UserOnlineSerializer


class UserCourseViewSet(viewsets.ModelViewSet):
    queryset = UserCourse.objects.all()
    serializer_class = UserCourseSerializer


class UserFeedbackViewSet(viewsets.ModelViewSet):
    """
    用户反馈
    """
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    filter_fields = ('username', 'school', 'grade', 'klass', 'create_time', 'content', 'title',)


class UserPositionViewSet(viewsets.ModelViewSet):
    """
    用户位置信息
    """
    queryset = UserPosition.objects.all()
    serializer_class = UserPositionSerializer
    filter_fields = ('id', 'user', 'user__username',)


class UserScenariosRopViewSet(viewsets.ModelViewSet):
    """
    用户情景介绍记录
    """
    queryset = UserScenariosReport.objects.filter(is_active=True)
    serializer_class = UserScenariosRopSerializer
    permission_classes = (OnlyTeacher,)
    filter_fields = ('teacher', 'unit')

    @list_route(methods=['POST'])
    def report_user_scenarios(self, request):
        """
        用户情景介绍记录
        :param request:

            {
                "teacher_id": 5,
                "unit_id": 1
            }
        :return:
        """
        teacher_id = request.data.get('teacher_id')
        unit_id = request.data.get('unit_id')
        try:
            BigfishUser.objects.get(id=teacher_id)
            Unit.objects.get(id=unit_id)
        except:
            return Response(rsp_msg_400('用户或单元id不存在'), status=status.HTTP_200_OK)
        data = {'teacher_id': teacher_id, 'unit_id': unit_id}
        # obj, created = UserScenariosReport.objects.update_or_create(defaults=data, **data)
        try:
            user_report = UserScenariosReport.objects.get(teacher_id=teacher_id, unit_id=unit_id, is_active=True)
            return Response(rsp_msg_200({'report_id': user_report.id}), status=status.HTTP_200_OK)
        except:
            UserScenariosReport.objects.create(**data)
            return Response(rsp_msg_200(), status=status.HTTP_200_OK)


class SNRegisterView(RegisterView):
    """
    通过序列注册用户

    :param request:\n

       {
          "username": "test_sn2",
          "encrypt_sn": "sda23sads4",
          "password1": "123456",
          "password2": "123456",
          "realname": "序列用户",
          "klass_list":[1,2,3]
        }

    :return:\n
        {
            "key": "7fcc99150a4421b99115cf01251b262e93f09370"
        }
    """
    serializer_class = SNRegisterSerializer
    permission_classes = (AllowAny,)
    token_model = TokenModel

    def create(self, request, *args, **kwargs):
        encrypt_sn = request.data.pop("encrypt_sn", None)
        try:
            rs = RegisterSerial.objects.get(encrypt_sn=encrypt_sn, is_active=True)
        except Exception as e:
            raise BFValidationError("序列无效")
        klass_list = request.data.pop("klass_list", None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            # 1.创建用户
            user = self.perform_create(serializer)
            # 2.创建用户班级关系
            uk_list = []
            for klass in klass_list:
                uk_list.append(UserKlassRelationship(klass_id=klass, user=user))
            UserKlassRelationship.objects.bulk_create(uk_list)
            # 3.序列设置为无效
            rs.is_active = False
            rs.save()
        headers = self.get_success_headers(serializer.data)
        token = self.get_response_data(user)
        ret_data = {"key": token, "username": user.username, "password": "123456"}
        return Response(rsp_msg_200(ret_data),
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class BigFishSessionView(GenericAPIView):
    # permission_classes = (AllowAny,)
    serializer_class = BigFishSessionSerializer
    token_model = TokenModel
    queryset = BigFishSession

    def post(self, request, *args, **kwargs):
        account_id = request.user.id
        registration_id = request.data.get('registration_id', None)
        login_time = request.data.get('login_time', '')
        if not registration_id:
            raise BFValidationError("未传入设备ID")
        # 检查是否有其他设备登录
        current_session = BigFishSession.objects.filter(is_active=True, account_id=request.user.id).exclude(
            registration_id=registration_id)
        if current_session.exists():  # 有其他设备则发送通知给其他设备
            content = "大侠:您的账号于{}在另一台设备上登录,如非本人登录，建议前往个人中心修改密码！!".format(login_time)
            normal_send_message(get_json_data(1, content, account_id),
                                current_session.values_list('registration_id', flat=True))
        # 记录本次登录
        BigFishSession.objects.update_or_create(defaults={"is_active": True, "login_time": login_time},
                                                **{"registration_id": registration_id, "account_id": account_id})
        UserReg.objects.update_or_create(defaults={"registration_id": registration_id}, **{"user_id": account_id})
        # 将其他设备状态更为无效
        current_session.update(**{"is_active": True})
        return Response(rsp_msg_200(), status=status.HTTP_200_OK)
