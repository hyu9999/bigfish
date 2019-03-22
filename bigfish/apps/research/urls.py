from rest_framework import routers

from bigfish.apps.research.views import PrepareLessonViewSet, PrepareLessonReplyViewSet, PrepareLessonWatchViewSet, \
    TeachingLogViewSet, TeachingLogReplyViewSet, TeachingLogWatchViewSet, ResearchActivityViewSet, \
    ResearchActivityReplyViewSet, ResearchActivityWatchViewSet, TeacherScheduleViewSet, SchoolWeekViewSet

router = routers.SimpleRouter()
router.register(r'preparelesson', PrepareLessonViewSet)
router.register(r'preparelessonreply', PrepareLessonReplyViewSet)
router.register(r'preparelessonwatch', PrepareLessonWatchViewSet)
router.register(r'teachinglog', TeachingLogViewSet)
router.register(r'teachinglogreply', TeachingLogReplyViewSet)
router.register(r'teachinglogwatch', TeachingLogWatchViewSet)
router.register(r'researchactivity', ResearchActivityViewSet)
router.register(r'researchactivityreply', ResearchActivityReplyViewSet)
router.register(r'researchactivitywatch', ResearchActivityWatchViewSet)
router.register(r'teacherschedule', TeacherScheduleViewSet)
router.register(r'school_week', SchoolWeekViewSet)
# router.register(r'term_schedule', TermScheduleViewSet)

urlpatterns = router.urls
