from rest_framework import routers

from bigfish.apps.operation.views import OperationRecordViewSet, ActClickViewSet

router = routers.SimpleRouter()
router.register(r'operation_record', OperationRecordViewSet)
router.register(r'act_click', ActClickViewSet)
urlpatterns = router.urls
