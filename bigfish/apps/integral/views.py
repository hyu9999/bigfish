from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.integral.models import UserIntegral, IntegralReport
from bigfish.apps.integral.serializers import UserIntegralSerializer, IntegralReportSerializer
from bigfish.base import viewsets
from bigfish.base.ret_msg import rsp_msg_200
from bigfish.base import status

class UserIntegralViewSet(viewsets.ModelViewSet):
    """
    用户积分
    """
    queryset = UserIntegral.objects.all()
    serializer_class = UserIntegralSerializer
    filter_fields = ('user', 'user__username')


class IntegralReportViewSet(viewsets.ModelViewSet):
    """
    用户积分
    """
    queryset = IntegralReport.objects.all()
    serializer_class = IntegralReportSerializer
    filter_fields = ('user', 'user__username')

    @list_route(methods=['POST'])
    def save_user_integral(self, request):
        user_id = request.data.get('user_id', None)
        integral = request.data.get('integral', 0)
        status_data = request.data.get('status_data', 1)
        scene = request.data.get('scene', 1)
        description = request.data.get('description', '')
        if user_id is None:
            user_id = request.user.id
        integral_data = {'user_id': user_id, 'integral': integral, 'status': status_data, 'scene': scene,
                         'description': description}
        IntegralReport.objects.create(**integral_data)
        # 存储用户积分表
        user_integral, _ = UserIntegral.objects.get_or_create(defaults={}, **{'user_id': user_id})
        integral_data = user_integral.total + integral
        real = user_integral.real + integral
        user_integral_data = {'total': integral_data, 'real': real}
        UserIntegral.objects.update_or_create(defaults=user_integral_data, **{'user_id': user_id})
        return Response(rsp_msg_200(), status=status.HTTP_200_OK)




