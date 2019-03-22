from rest_framework import routers

from bigfish.apps.integral.views import UserIntegralViewSet, IntegralReportViewSet

router = routers.SimpleRouter()

router.register('userintegral', UserIntegralViewSet)
router.register('integral_report', IntegralReportViewSet)

urlpatterns = router.urls
