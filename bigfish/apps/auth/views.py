import datetime
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from rest_auth.app_settings import LoginSerializer
from rest_auth.models import TokenModel
from rest_auth.registration.views import sensitive_post_parameters_m
from rest_auth.views import LoginView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from bigfish.apps.bigfish.backend.hf_api.api import HFApi
from bigfish.apps.users.models import BigfishUser
from bigfish.apps.users.serializers import UserSerializer
from bigfish.apps.xiwo.models import SerialBindingRelation
from bigfish.base.const import TEACHER, STUDENT
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400, rsp_msg

logger = logging.getLogger('django')


class SSOAuthView(GenericAPIView):
    """
    SSO登录

    """
    queryset = None
    serializer_class = None

    def get(self, request):
        return Response("success", status=status.HTTP_200_OK)


class BigfishLoginView(LoginView):
    """
    大渔登录接口
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(BigfishLoginView, self).dispatch(*args, **kwargs)

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(rsp_msg_200(serializer.data), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        大渔登录接口

        :param request:\n
            - 普通登录
            {
              "username": "string",
              "password": "string"
            }
            - 根据设备ID自动登录
            {
              "registration_id": "string"
            }
            - 西沃 根据序列号和机器码登录
            {
              "serial_num": "string",
              "device_code": "string"
            }
        :return:\n
            {
              "code": 200,
              "data": {
                "key": "37c523b841c9e66288bfed90e47e39b81471310c"
              },
              "message": "success"
            }
        """
        self.request = request
        # extra
        registration_id = self.request.data.get('registration_id', None)
        # 根据设备ID登录
        if "registration_id" in self.request.data.keys():
            self.request.data.pop('registration_id', None)
            if not registration_id:
                return Response({"detail": "请传入设备ID！", "code": 400}, status=status.HTTP_200_OK)
            kwargs = {"reg__registration_id": registration_id}
            self.generate_user_info(**kwargs)
        # 根据序列号和机器码登录
        elif "serial_num" in self.request.data.keys() and "device_code" in self.request.data.keys():
            serial_num = self.request.data.get('serial_num', None)
            device_code = self.request.data.get('device_code', None)
            self.request.data.pop('serial_num', None)
            self.request.data.pop('device_code', None)
            bind_status, is_invalid, user = self.check_bind(serial_num, device_code)
            if not bind_status:
                raise BFValidationError("该设备暂未绑定序列号！")
            if is_invalid:
                raise BFValidationError("当前设备已过期，请联系管理员进行续费！")
            try:
                self.request.data['username'] = user.username
            except Exception as e:
                logger.error(e)
                raise BFValidationError("获取绑定用户信息失败！")
            self.request.data['password'] = '123456'
        # 正常登录
        else:
            self.request.data.pop('registration_id', None)
            self.update_registration(registration_id)
        # end
        username = self.request.data.get('username', None)
        password = self.request.data.get('password', None)
        user = authenticate(username=username, password=password)
        if user:
            self.serializer = self.get_serializer(data=self.request.data)
            self.serializer.is_valid(raise_exception=True)
            self.login()
            return self.get_response()
        else:
            return Response(rsp_msg(msg="用户名或密码错误，请查证后登陆！", code=status.HTTP_401_UNAUTHORIZED),
                            status=status.HTTP_200_OK)

    @classmethod
    def get_random_username(cls, flag='bigfish'):
        # 希沃账号登录
        if flag == 'xiwo':
            queryset = BigfishUser.objects.filter(identity=TEACHER, username__startswith='xw')
            suffix = queryset.count() + 1
            username = "xw" + "{}".format(suffix).zfill(6)
        # 根据设备ID登录
        else:
            queryset = BigfishUser.objects.filter(identity=STUDENT)
            suffix = queryset.count() + 1
            username = "{}".format(suffix).zfill(8)
        return username

    def generate_user_info(self, flag="bigfish", **kwargs):
        # 根据设备ID登录账户
        if flag == 'xiwo':
            identity = TEACHER  # 老师
        else:
            identity = STUDENT  # 学生
        try:
            instance = BigfishUser.objects.select_related('reg').get(**kwargs)
        except Exception as e:
            logger.debug(e)
            username = self.get_random_username(flag)
            password = '123456'
            self.request.data['username'] = username
            self.request.data['password'] = password

            data = {
                "username": username,
                "password": password,
                "identity": identity,
                "sex": 1,
                'icon': '/media/headericon/default.png',
                "realname": "用户{}".format(username),
                "reg": {
                    "user": 0,
                    "registration_id": kwargs.get("reg__registration_id", None)
                }

            }
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            username = instance.username
            password = '123456'
            self.request.data['username'] = username
            self.request.data['password'] = password

    def update_registration(self, registration_id):
        try:
            user_profile = BigfishUser.objects.get(username=self.request.data.get('username', None))
            old_registration_id = user_profile.registration_id
        except Exception as e:
            logger.debug(e)
        else:
            if registration_id != old_registration_id:
                user_profile.registration_id = registration_id
                user_profile.save()

    @staticmethod
    def check_bind(serial_num, device_code):
        bind_status, is_invalid = True, True
        serial_num = int(serial_num, base=32)
        user = None
        try:
            sbr = SerialBindingRelation.objects.get(serial_num__serial_num=serial_num, device_code=device_code)
        except Exception as e:
            logger.debug(e)
            bind_status = False
        else:
            user = sbr.user
            current_time = datetime.datetime.now()
            if sbr.invalid_time > current_time:
                is_invalid = False
        return bind_status, is_invalid, user


class LoginExamine(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        将前一次登录强制退出

        :param request:

            {
                "username": 20730002,
                "password": 123456
            }
        :return:
        """
        username = request.data.get('username')
        password = request.data.get('password')
        source = request.data.get('source', 'pc')
        user_obj = authenticate(username=username, password=password)
        if user_obj is not None:
            try:
                user = BigfishUser.objects.get(username=username)
            except:
                return Response(rsp_msg_400('用户不存在'), status=status.HTTP_200_OK)
            if source == 'Android':
                pass
            elif source == 'pc':
                Token.objects.filter(user=user).delete()
            return Response(rsp_msg_200({'identity': user.identity}), status=status.HTTP_200_OK)
        else:
            return Response(rsp_msg_400('用户名或密码错误，请查证后登陆！'), status=status.HTTP_200_OK)


class GetServerTime(APIView):

    def get(self, request):
        """
        获取服务器当前时间

        :param request:
        :return:

            {
              "data": {
                "server_time": "2019-03-02 13:32:11"
              },
              "message": "success",
              "code": 200
            }
        """
        # 返回服务器时间 pc端获取不到
        result = {'server_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)


class HFLoginView(LoginView):
    """
    恒峰登录接口
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(HFLoginView, self).dispatch(*args, **kwargs)

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(rsp_msg_200(serializer.data), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        恒峰登录接口

        :param request:\n
            {
                "access_token": "xcxzc-zxcxzc-zczc-xzczcz"
            }
        :return:\n
            {
              "code": 200,
              "data": {
                "key": "37c523b841c9e66288bfed90e47e39b81471310c"
              },
              "message": "success"
            }
        """
        # 1.根据accessToken校验hf登录是否正常
        access_token = self.request.data.get("access_token", None)
        if not access_token:
            return Response(rsp_msg_400("请传入正确的access_token！"), status=status.HTTP_200_OK)
        hf = HFApi(access_token=access_token)
        try:
            api_token_info = hf.get_api_token()
            api_token = api_token_info.get("data").get("apiToken")
            user_info = hf.get_user_info(api_token)
            username = user_info.get("data").get("username")
            password = 'hf@2019'
        except Exception as e:
            logger.error(e)
            return Response(rsp_msg_400("token校验失败！"), status=status.HTTP_200_OK)
        # 2.获取用户信息
        self.request.data["username"] = username
        self.request.data['password'] = password
        user = authenticate(username=username, password=password)
        if user:
            self.serializer = self.get_serializer(data=self.request.data)
            self.serializer.is_valid(raise_exception=True)
            self.login()
            return self.get_response()
        else:
            return Response(rsp_msg(msg="用户名或密码错误，请查证后登陆！", code=status.HTTP_401_UNAUTHORIZED),
                            status=status.HTTP_200_OK)
