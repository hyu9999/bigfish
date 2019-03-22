from rest_framework import routers

from bigfish.apps.knowledgepoint.views import KnowledgePointViewSet

router = routers.SimpleRouter()
router.register('knowledge_point', KnowledgePointViewSet)

urlpatterns = router.urls
