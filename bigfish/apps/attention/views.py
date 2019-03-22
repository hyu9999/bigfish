import logging

from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.attention.models import AttentionCircle
from bigfish.apps.attention.serializers import AttentionCircleSerializer, ACFocusSerializer
from bigfish.apps.dubbing.models import UserDubbing, DubbingZan, DubbingRead
from bigfish.apps.dubbing.serializers import UserDubbingSerializer
from bigfish.apps.schools.models import Klass
from bigfish.apps.users.models import BigfishUser
from bigfish.apps.users.serializers import UserSerializer
from bigfish.base import viewsets
from bigfish.base.const import PAGE_NUM
from bigfish.base.ret_msg import rsp_msg_200
from bigfish.utils.paginations import common_paging_bj

logger = logging.getLogger('django')


class AttentionCircleViewSet(viewsets.ModelViewSet):
    serializer_class = AttentionCircleSerializer
    queryset = AttentionCircle.objects.all()

    @list_route(methods=["POST"])
    def create_attention(self, request):
        """
        创建用户关注数据：post：{other：1}
        """
        user = request.user
        other = request.data.get('other')
        try:
            other_obj = BigfishUser.objects.get(id=other)
        except Exception as e:
            print(e)
            return Response({"data": [], "message": "传入的用户不存在，id={}！".format(other), "code": 400}, status=200)
        if other == user.id:
            return Response({"data": [], "message": "自己不能关注自己！", "code": 400}, status=200)
        if not other:
            return Response({"data": [], "message": "fans是必传字段！", "code": 400}, status=200)
        at_data = {
            'user': other,
            'fans': user.id
        }
        try:
            AttentionCircle.objects.create(**at_data)
        except Exception as e:
            print(e)
            return Response({"data": [], "message": "已经关注过此用户！", "code": 400}, status=200)
        other_obj.profile.fans_num += 1
        other_obj.profile.save()
        user.profile.attention_num += 1
        user.profile.save()
        return Response({"data": [], "message": "关注成功！", "code": 200}, status=200)

    @list_route(methods=["GET"])
    def get_attention_list(self, request, *args, **kwargs):
        """
        获取用户关注数据

        :param request:\n
        :param args:\n
        :param kwargs:\n
        :return: \n
            {
                "message": "success",
                "code": 200,
                "data": {
                    "count": 2,
                    "next": "http://localhost:8000/api/attention/attentioncircle/get_attention_list/?page=2&page_size=1",
                    "previous": null,
                    "results": [
                        {
                            "id": 5,
                            "realname": "用户00000001",
                            "icon": "",
                            "each_other": false
                        }
                    ]
                }
            }
        """
        queryset = self.get_queryset().filter(fans=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ACFocusSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ACFocusSerializer(queryset, many=True)
        return Response(rsp_msg_200(serializer.data), status=status.HTTP_200_OK)

    @list_route(methods=["GET"])
    def get_fans_list(self, request):
        """
        获取用户粉丝数据：get：page：列表页码
        """
        user = request.GET.get('user', 0)
        page = request.GET.get('page', 0)
        page = int(page)
        if page >= 1:
            page -= 1
        start = int(page) * PAGE_NUM
        end = start + PAGE_NUM
        results = []
        data_list = AttentionCircle.objects.filter(user=user)
        page_list = data_list[start:end]
        for other in page_list:
            try:
                user_obj = BigfishUser.objects.get(id=other.fans)
            except Exception as e:
                print(e)
                return Response({"data": [], "detail": {}, "message": "用户数据错误，id={}！".format(other.fans),
                                 "code": 400}, status=200)
            user_data = UserSerializer(user_obj).data
            other_fans = AttentionCircle.objects.filter(user=other.fans, fans=user).count()
            if other_fans > 0:
                user_data['is_eachother'] = True
            elif other_fans == 0:
                user_data['is_eachother'] = False
            klass_id = user_data['profile']['default_cid']
            try:
                klass_obj = Klass.objects.get(id=klass_id)
                user_data['klass_name'] = klass_obj.grade + klass_obj.name
                user_data['school_name'] = klass_obj.school.name
            except Exception as e:
                logger.debug(e)
                user_data['klass_name'] = ""
                user_data['school_name'] = ""
            user_data['attention_num'] = user_data['profile']['attention_num']
            user_data['fans_num'] = user_data['profile']['fans_num']
            user_data.pop("klass_detail")
            results.append(user_data)
        at_info = {}
        at_info['total'] = data_list.count()
        at_info['page_num'] = PAGE_NUM
        return Response({"data": results, "detail": at_info, "message": "success", "code": 200}, status=200)

    @list_route(methods=["GET"])
    def is_each_other_attention(self, request):
        """
        获取两个用户间相互关注的状态：0：相互没有粉；1：user粉了other；2：other粉了other；3：互粉
        """
        user = request.GET.get('user')
        other = request.GET.get('other')
        user_fans = AttentionCircle.objects.filter(user=user, fans=other).count()
        other_fans = AttentionCircle.objects.filter(user=other, fans=user).count()
        user_data = 0
        if user_fans == 0 and other_fans == 0:
            user_data = 0
        elif user_fans > 0 and other_fans == 0:
            user_data = 1
        elif user_fans == 0 and other_fans > 0:
            user_data = 2
        elif user_fans > 0 and other_fans > 0:
            user_data = 3
        return Response(rsp_msg_200(user_data), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_friends_circle(self, request):
        user = request.user
        at_list = AttentionCircle.objects.filter(fans=user.id)
        user_list = []
        for uf in at_list:
            user_list.append(uf.user)
        ud_list = UserDubbing.objects.filter(user__in=user_list, is_active=True).order_by('-create_time')
        ud_data = UserDubbingSerializer(ud_list, many=True).data
        for ud in ud_data:
            try:
                zan_obj = DubbingZan.objects.get(userdubbing=ud['id'], user=user)
                ud['is_zan'] = True
            except Exception as e:
                ud['is_zan'] = False
        item_list = DubbingRead.objects.filter(user=user.id)
        for item in item_list:
            item.is_read = True
            item.save()
        page = common_paging_bj(ud_data, request)
        return Response(rsp_msg_200(extra=page), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_show_red(self, request):
        user = request.user
        ur_list = DubbingRead.objects.filter(user=user, is_read=False)
        if ur_list:
            return Response({"data": True, "message": "success", "code": 200}, status=200)
        else:
            return Response({"data": False, "message": "success", "code": 200}, status=200)
