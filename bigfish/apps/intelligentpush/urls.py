from rest_framework import routers

from bigfish.apps.intelligentpush.views import IntelligentPushViewSet

router = routers.SimpleRouter()
router.register(r'intelligent', IntelligentPushViewSet)

urlpatterns = router.urls