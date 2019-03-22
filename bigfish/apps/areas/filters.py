from django_filters.rest_framework import filterset

from bigfish.apps.areas.models import Area


class AreaFilter(filterset.FilterSet):
    class Meta:
        model = Area
        fields = {
            "coding": ["exact"],
            "level": ["exact"],
            "name": ["exact", "contains"],
            "prov_code": ["exact"],
            "city_code": ["exact"],
            "is_active": ["exact"]
        }
