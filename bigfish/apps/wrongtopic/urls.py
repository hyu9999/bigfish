from rest_framework import routers

from bigfish.apps.wrongtopic.views import WrongTopicHisViewSet, WrongTopicViewSet

router = routers.SimpleRouter()
router.register(r'wrongtopic', WrongTopicViewSet)
router.register(r'wrongtopic_his', WrongTopicHisViewSet)

urlpatterns = router.urls