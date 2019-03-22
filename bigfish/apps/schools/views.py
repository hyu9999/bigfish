import logging

from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.schools.models import School, Term, SchoolTerm, SchoolWeek, TermWeek, Klass, KlassProgress, \
    KlassActProgress, RegisterSerial
from bigfish.apps.schools.serializers import SchoolSerializer, TermSerializer, SchoolTermSerializer, \
    SchoolWeekSerializer, TermWeekSerializer, KlassBaseSerializer, KlassProgressSerializer, \
    KlassActProgressMinSerializer, RegisterSerialSerializer
from bigfish.apps.users.models import UserKlassRelationship
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_400, rsp_msg_200

logger = logging.getLogger('django')


class TermViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class SchoolTermViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = SchoolTerm.objects.all()
    serializer_class = SchoolTermSerializer


class SchoolWeekViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = SchoolWeek.objects.all()
    serializer_class = SchoolWeekSerializer


class TermWeekViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = TermWeek.objects.all()
    serializer_class = TermWeekSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_fields = {
        "id": ["exact"],
        "coding": ["exact"],
        "title": ["exact", "contains"],
        "areas_id": ["exact"],
        "is_normal": ["exact", "contains"],
    }


class KlassViewSet(viewsets.ModelViewSet):
    queryset = Klass.objects.all().order_by('order')
    serializer_class = KlassBaseSerializer

    @list_route(methods=["POST"])
    def change_default_klass(self, request):
        """
        修改默认班级
        :param request: \n
            {
                "klass_id": 1,
                "user_id":1
            }
        :return: \n
        """
        user_id = request.data.get('user_id', None)
        if not user_id:
            user_id = request.user.id
        # 需要设置为默认班级的id
        klass_id = request.data.get('klass_id', None)
        if klass_id is None:
            return Response(rsp_msg_400('请传入要修改的班级id'), status=status.HTTP_200_OK)
        try:
            user_klass = UserKlassRelationship.objects.get(user_id=user_id, is_default=True,
                                                           is_effect=True)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400('获取用户默认班级有误'), status=status.HTTP_200_OK)
        #  传入不是默认班级 就进行修改
        if not user_klass.klass.id == klass_id:
            user_klass.is_default = False
            user_klass.save()
            try:
                UserKlassRelationship.objects.filter(user_id=user_id,
                                                     klass_id=klass_id, is_effect=True).update(**{'is_default': True})
            except:
                return Response(rsp_msg_400('班级不存在'), status=status.HTTP_200_OK)
        return Response(rsp_msg_200(), status=status.HTTP_200_OK)


class KlassProgressViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = KlassProgress.objects.all()
    serializer_class = KlassProgressSerializer


class KlassActProgressViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = KlassActProgress.objects.all()
    serializer_class = KlassActProgressMinSerializer
    filter_fields = ('klass_id', 'lesson_id', 'act_tab_id', 'is_finish', 'activity_id')


class RegisterSerialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = RegisterSerial.objects.all()
    serializer_class = RegisterSerialSerializer
    filter_fields = '__all__'

    @list_route()
    def check_sn(self, request):
        """
        校验序列

        :param request:\n
            encrypt_sn=ad8da7d
        :return:\n
            {
              "data": {
                "flag": false,
                "school_id": 0
              },
              "message": "success",
              "code": 200
            }
        """
        encrypt_sn = request.query_params.get("encrypt_sn", None)
        ret_data = {"flag": False, "school_id": 0}
        if not encrypt_sn:
            raise BFValidationError("请传入序列")
        try:
            rs = RegisterSerial.objects.get(encrypt_sn=encrypt_sn)
        except Exception as e:
            logger.info(e)
        else:
            ret_data["school_id"] = rs.school_id
            ret_data["flag"] = rs.is_active
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
