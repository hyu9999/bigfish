import datetime
import os
from urllib.parse import urlsplit

from django.contrib.auth.models import User
from django.db.models import Max
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bigfish.apps.users.models import BigfishUser
from bigfish.apps.versionupdate.models import Version, UpdateConfig, UpdateException, UpdateDetail, IdentityVersion, \
    UpdatePublish
from bigfish.apps.versionupdate.serializers import VersionSerializer
from bigfish.base import viewsets, status
from bigfish.base.const import MEDIA_VERSION_DIR
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400
from bigfish.settings.base import MEDIA_ROOT


class VersionViews(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (AllowAny,)

    @list_route(methods=['GET'])
    def update_version(self, request):
        """
        更新版本
        :param request: \n
            {
              "user_name": "10720001"
            }
        :return: \n
            {
                "data": {
                    "version_name": "1.2.7",
                    "apk_size": 30140,
                    "message": "1231qweqw",
                    "apk_code": 20,
                    "version_code": 1,
                    "folder_name": "http://127.0.0.1:8000/media/version/1.2.7/SuperFishTeacher.apk"
                },
                "message": "success",
                "code": 200
            }
        """
        user_name = request.GET.get('user_name', None)
        try:
            user = BigfishUser.objects.get(username=user_name)
        except:
            return Response(rsp_msg_400('该用户不存在'), status=status.HTTP_200_OK)
        version = Version.objects.all().order_by('-version_code').first()
        # max_version_code = Version.objects.all().aggregate(max_code=Max('version_code')).get('max_code', 0)
        # if max_apk_code is None:
        #     return Response(rsp_msg_400('用户版本配置有误'), status=status.HTTP_200_OK)
        # if apk_code >= max_apk_code:
        #     # 返回参数下个版本进行修改
        #     return Response(rsp_msg_200({'message': '已经是最新版本'}), status=status.HTTP_200_OK)
        # else:
        try:
            identity_version = IdentityVersion.objects.get(identity=user.identity,
                                                           version=version)
        except Exception as e:
            return Response(rsp_msg_400('获取角色对应版本失败'), status=status.HTTP_200_OK)
        data = {'version_name': identity_version.version.version_name, 'message': identity_version.note,
                'folder_name': splice_path(request, identity_version.folder_name, identity_version.apk_name),
                'apk_size': identity_version.apk_size, 'apk_code': version.apk_code, 'version_code': version.version_code}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def update_exception(self, request):
        """
        更新异常记录
        :param request: \n
            {
              "version_name": "1.1.1",
              "user_name": "10720001",
              "message": "错误信息",
              "note": "备注"
            }
        :return: \n
        """
        version_name = request.data.get('version_name', None)
        user_name = request.data.get('user_name')
        message = request.data.get('message', '')
        note = request.data.get('note', '')
        try:
            version = Version.objects.get(version_name=version_name)
            user = BigfishUser.objects.get(username=user_name)
        except:
            return Response(rsp_msg_400('版本号或用户不存在'), status=status.HTTP_200_OK)
        try:
            identity = IdentityVersion.objects.get(identity=user.profile.identity, version=version)
        except:
            return Response(rsp_msg_400('角色版本不存在'), status=status.HTTP_200_OK)
        publish = UpdatePublish.objects.get(identity=identity, publish=user.profile.attend_class.first().publish)
        data = {'version': version, 'username': user_name, 'message': message, 'note': note,
                'identity': identity,
                'publish': user.profile.attend_class.first().publish,
                'update_publish': publish
                }
        try:
            UpdateException.objects.create(**data)
        except:
            return Response(rsp_msg_400('更新异常记录存储错误'), status=status.HTTP_200_OK)
        else:
            return Response(rsp_msg_200({'message': '异常记录存储成功'}), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def update_resource(self, request):
        """
        更新资源
        :param request: \n
            {
              "user_name": "20730001",
              "version_code":"1",
            }
        :return: \n

           {
              "data": [
                {
                  "change_size": 1001,
                  "last_size": 2,
                  "version_code": "0",
                  "folder_name": "/media/version/2.0.1/media.zip",
                  "current_size": 1001,
                  "operate": 2
                }
              ],
              "message": "success",
              "code": 200
            }
        """
        user_name = request.data.get('user_name', None)
        version_code = request.data.get('version_code', None)
        try:
            user = BigfishUser.objects.get(username=user_name)
        except:
            return Response(rsp_msg_400('用户不存在'), status=status.HTTP_200_OK)
        version_queryset = Version.objects.filter(version_code__gt=int(version_code))
        max_version_code = Version.objects.all().aggregate(max_code=Max('version_code')).get('max_code', 0)
        data = []
        for version in version_queryset:
            try:
                identity_version = IdentityVersion.objects.get(version=version, identity=user.identity)
                publish = UpdatePublish.objects.get(publish=user.attend_class.first().publish, identity=identity_version)
            except:
                return Response(rsp_msg_400('角色版本或更新教材配置错误'), status=status.HTTP_200_OK)
            detail_queryset = UpdateDetail.objects.filter(update_publish=publish)
            if detail_queryset.exists():
                for detail in detail_queryset:
                    version_name = version.version_name
                    version_dir = os.path.join(MEDIA_ROOT, version_name)
                    if not os.path.exists(version_dir):
                        os.makedirs(version_dir)
                    data.append(
                        {'resource_path': resource_path(MEDIA_VERSION_DIR, version_name, detail.zip_name),
                         'current_size': detail.surrent_size, 'last_size': detail.last_size,
                         'change_size': detail.change_size, 'operate': detail.operate})
        result = {'version_code': max_version_code, 'data': data}
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)


def splice_path(request, *args):
    http = urlsplit(request.build_absolute_uri(None)).scheme
    path = http + '://' + request.get_host() + '/'.join(args)
    return path


def resource_path(*args):
    """
    资源路径 前端拼域名
    :param args:
    :return:
    """
    path = '/'.join(args)
    return path









