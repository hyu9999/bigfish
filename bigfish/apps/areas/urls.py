from rest_framework import routers

from bigfish.apps.areas.views import AreaViewSet

router = routers.SimpleRouter()

router.register('area', AreaViewSet)

urlpatterns = router.urls
