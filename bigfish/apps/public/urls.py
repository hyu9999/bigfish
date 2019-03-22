from rest_framework import routers

from bigfish.apps.public.views import PublicViewSet, AppTableViewSet, ATGroupViewSet

router = routers.SimpleRouter()
router.register(r'public', PublicViewSet)
router.register(r'at_group', ATGroupViewSet)
router.register(r'app_table', AppTableViewSet)

urlpatterns = router.urls
