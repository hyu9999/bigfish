from rest_framework import routers

from bigfish.apps.schools.views import KlassViewSet, KlassProgressViewSet, TermViewSet, SchoolTermViewSet, \
    SchoolWeekViewSet, TermWeekViewSet, SchoolViewSet, KlassActProgressViewSet, RegisterSerialViewSet

router = routers.SimpleRouter()
router.register('term', TermViewSet)
router.register('schoolterm', SchoolTermViewSet)
router.register('schoolweek', SchoolWeekViewSet)
router.register('termweek', TermWeekViewSet)
router.register('school', SchoolViewSet)
router.register('klass', KlassViewSet)
router.register('klassprogress', KlassProgressViewSet)
router.register('klass_act_progress', KlassActProgressViewSet)
router.register('register_serial', RegisterSerialViewSet)
urlpatterns = router.urls