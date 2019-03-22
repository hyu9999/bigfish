from rest_framework import routers

from bigfish.apps.questions.views import QuestionViewSet, QuestionKPRelationshipViewSet

router = routers.SimpleRouter()
router.register('question_knowledge_point', QuestionKPRelationshipViewSet)
router.register('questions', QuestionViewSet)

urlpatterns = router.urls
