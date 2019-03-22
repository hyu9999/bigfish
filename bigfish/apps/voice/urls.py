from rest_framework import routers

from bigfish.apps.voice.views import SpeechEvaluationReportViewSet

router = routers.SimpleRouter()
router.register('speech_evaluation_report', SpeechEvaluationReportViewSet)

urlpatterns = router.urls
