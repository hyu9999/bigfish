from rest_framework import routers

from bigfish.apps.classrooms.views import BlackSettingViewSet, BlackSettingReportViewSet, CastViewSet, \
    CastReportViewSet, ClassroomViewSet, ActivityReportViewSet, \
    ActivityDetailReportViewSet

router = routers.SimpleRouter()

router.register('blacksetting', BlackSettingViewSet)
router.register('blacksetting_report', BlackSettingReportViewSet)
router.register('cast', CastViewSet)
router.register('cast_report', CastReportViewSet)
router.register('classroom', ClassroomViewSet)
router.register('activity_report', ActivityReportViewSet)
router.register('activitydetail_report', ActivityDetailReportViewSet)

urlpatterns = router.urls
