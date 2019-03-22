from rest_framework import routers
from bigfish.apps.versionupdate.views import VersionViews

router = routers.SimpleRouter()
router.register(r'version', VersionViews)

urlpatterns = router.urls