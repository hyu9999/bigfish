import datetime
import logging

from django.db import transaction
from rest_framework.decorators import list_route, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bigfish.apps.schools.models import Klass
from bigfish.apps.users.models import BigfishUser
from bigfish.apps.users.serializers import UserSerializer
from bigfish.apps.xiwo.models import SerialBindingRelation, SerialNum, SerialBindingReport
from bigfish.apps.xiwo.serializers import SerialBindingRelationSerializer
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200

logger = logging.getLogger("django")


class SerialBindingRelationViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a SerialBindingRelation instance.
    list:
        Return all SerialBindingRelation, ordered by most recently joined.
    create:
        Create a new SerialBindingRelation.
    delete:
        Remove an existing SerialBindingRelation.
    partial_update:
        Update one or more fields on an existing SerialBindingRelation.
    update:
        Update a SerialBindingRelation.
    """
    queryset = SerialBindingRelation.objects.all()
    serializer_class = SerialBindingRelationSerializer

    @list_route(methods=["POST"])
    def extend_use_duration(self, request):
        """
        延长使用时间

        :param request:\n
            {
                "serial_num": "5cgk51",
                "extend_days":30
            }
        :return:\n
            {
              "detail": "延期成功！",
              "code": 200,
              "result": "success"
            }
        """
        # TODO 增加限制：每分钟只可提交一次，避免重复提交
        serial_num_32 = request.data.get("serial_num", None)
        extend_days = request.data.get("extend_days", None)
        if not serial_num_32 or not extend_days:
            raise BFValidationError("传入参数异常！")
        else:
            serial_num = int(serial_num_32, base=32)
        ret_msg = "延期成功！"
        try:
            sn = SerialNum.objects.get(serial_num=serial_num)
        except Exception as e:
            logger.debug("未查询到该序列号！[{}]".format(e))
            raise BFValidationError('传入序列号不存在！')
        try:
            sbr = SerialBindingRelation.objects.get(serial_num=sn)
        except Exception as e:
            logger.debug("未查询到该绑定关系！[{}]".format(e))
            raise BFValidationError("未查询到该绑定关系！")

        bind_time = datetime.datetime.now()
        invalid_time = bind_time + datetime.timedelta(days=sn.level.effect_duration)
        # 已过期
        if sbr.invalid_time < bind_time:
            sbr.invalid_time = invalid_time
            remark = "[延期]已过期!"
        else:
            sbr.invalid_time = sbr.invalid_time + datetime.timedelta(days=extend_days)
            remark = "[延期]未过期!"
        sbr.bind_status = 2
        sbr.save()
        # 记录更新历史
        his_param_list = {"serial_num": serial_num, "device_code": sbr.device_code, "change_times": sbr.change_times,
                          "bind_time": bind_time, "invalid_time": invalid_time, "remark": remark}
        SerialBindingReport.objects.create(**his_param_list)
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_serial_info(request):
    """
    获取序列信息

    :param request: \n
        serial_num=5cgk51
        \n
    :return:\n
        {
            "code": 200,
            "detail": {
                "add_time": "",
                "serial_num": "5cgk51",
                "user": null,
                "is_normal": false,
                "change_times": 1,
                "device_code": "",
                "bind_status": 1,
                "bind_time": "",
                "invalid_time": ""
            },
            "result": "success"
        }
    """
    serial_num_32 = request.query_params.get("serial_num", None)
    if not serial_num_32:
        raise BFValidationError("请传入序列号！")
    else:
        try:
            serial_num = int(serial_num_32, base=32)
        except Exception as e:
            raise BFValidationError("该序列号不符合规则！")
    try:
        sbr = SerialBindingRelation.objects.get(serial_num=serial_num)
    except Exception as e:
        logger.error(e)
        try:
            sn = SerialNum.objects.get(serial_num=serial_num)
        except Exception as e:
            raise BFValidationError("该序列号不存在！")
        else:
            data = {"serial_num": serial_num_32, "device_code": "", "bind_status": 1, "bind_time": "",
                    "invalid_time": "", "change_times": sn.max_times, "is_normal": False, "add_time": "", "user": None}
    else:
        data = SerialBindingRelationSerializer(sbr).data
    return Response(rsp_msg_200(data), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def bind_device(request):
    """
    机器码绑定

    :param request: \n
        {
            "serial_num": "5cgk51",
            "device_code": "xd9daud8asdua"
        }\n
    :return:\n
        {
          "result": "success",
          "detail": "绑定成功！",
          "code": 200
        }
    """
    serial_num_32 = request.data.get('serial_num', None)
    device_code = request.data.get('device_code', None)
    if not serial_num_32 or not device_code:
        raise BFValidationError("传入参数异常！")
    else:
        try:
            serial_num = int(serial_num_32, base=32)
        except Exception as e:
            raise BFValidationError("该序列号不符合规则！")
    try:
        sn = SerialNum.objects.get(serial_num=serial_num)
    except Exception as e:
        logger.debug("未查询到该序列号！[{}]".format(e))
        raise BFValidationError('传入序列号不存在！')
    # 绑定序列号
    bind_time = datetime.datetime.now()
    invalid_time = bind_time + datetime.timedelta(days=sn.level.effect_duration)
    his_param_list = {"serial_num": serial_num, "device_code": device_code}
    ret_msg = "绑定成功！"
    try:
        sbr = SerialBindingRelation.objects.get(serial_num__serial_num=serial_num)
    except Exception as e:
        logger.debug("未查询到绑定关系！[{}]".format(e))
        with transaction.atomic():
            # 创建西沃用户
            user_data = generate_xiwo_user()
            # 1.新建 绑定关系
            param_list = {
                "serial_num": sn, "device_code": device_code, "bind_status": 2, "bind_time": bind_time,
                "invalid_time": invalid_time, "user_id": user_data.get('id')
            }

            SerialBindingRelation.objects.create(**param_list)
            his_param_list['bind_time'] = bind_time
            his_param_list['invalid_time'] = invalid_time
            his_param_list['remark'] = "[绑定设备]新增绑定关系"

    else:
        old_device_code = sbr.device_code
        if old_device_code == device_code:
            raise BFValidationError("已绑定，无需再次绑定！")
        # 2.更新
        if sbr.change_times == sbr.serial_num.max_times:
            raise BFValidationError("绑定次数达到上限，无法继续绑定！")
        # 2.1 未绑定：直接绑定
        if sbr.bind_status == 1:
            sbr.bind_status = 2
            sbr.bind_time = bind_time
            sbr.invalid_time = invalid_time
            his_param_list['bind_time'] = bind_time
            his_param_list['invalid_time'] = invalid_time
            his_param_list['remark'] = "[绑定设备]未绑定状态改为绑定状态！"
        else:
            # 2.2 已过期
            if sbr.invalid_time < bind_time or sbr.bind_status == 3:
                raise BFValidationError("该序列号已过期，请延长使用时间！")
            # 2.3 已绑定：更换设备
            else:
                change_times = sbr.change_times + 1
                sbr.change_times = change_times
                his_param_list['old_device_code'] = old_device_code
                his_param_list['change_times'] = change_times
                ret_msg = "更换设备成功！"
                his_param_list['remark'] = "[绑定设备]更换设备！"
        sbr.device_code = device_code
        sbr.save()
    # 记录更新历史
    SerialBindingReport.objects.create(**his_param_list)
    return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)


def generate_xiwo_user():
    """
    生成xiwo用户

    :return:
    """
    username = get_random_username()
    password = '123456'

    data = {
        "username": username,
        "password": password,
        "profile": {
            "user": 0,
            "identity": "老师",
            "sex": "男生",
            'icon': '/media/headericon/default.png',
            "realname": "希沃{}".format(username),
            "lesson": 51,
            "is_pilot_user": True
        }
    }
    # create --user
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    # create --klass
    try:
        klass_list = Klass.objects.filter(school_id=78)  # 希沃小学
        # TODO 增加默认班级ID(后期需删除)
        default_cid = klass_list.first().id
        instance.profile.default_cid = default_cid
        instance.profile.textbook = 9
    except Exception as e:
        logger.exception(e)
    else:
        for klass in klass_list:
            instance.profile.attend_class.add(klass)
            instance.profile.save()
    return serializer.data


def get_random_username():
    """
    生成xiwo账号

    :return:
    """
    queryset = BigfishUser.objects.filter(identity='老师', user__username__startswith='xw')
    suffix = queryset.count() + 1
    username = "xw" + "{}".format(suffix).zfill(6)
    return username
