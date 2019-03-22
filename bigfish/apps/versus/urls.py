from rest_framework import routers

from bigfish.apps.versus.views import VersusDetailViewSet, VersusViewSet

router = routers.SimpleRouter()
router.register(r'versus', VersusViewSet)
router.register(r'versusdetail', VersusDetailViewSet)

urlpatterns = router.urls
