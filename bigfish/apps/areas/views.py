from bigfish.apps.areas.models import Area
from bigfish.apps.areas.serializers import AreaSerializer
from bigfish.base import viewsets


class AreaViewSet(viewsets.ModelViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all()
    filter_fields = ('coding', 'name', 'level', 'prov_code', 'city_code', 'is_active')
