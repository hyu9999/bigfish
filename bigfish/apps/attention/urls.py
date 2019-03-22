from rest_framework import routers

from bigfish.apps.attention.views import AttentionCircleViewSet

router = routers.SimpleRouter()

router.register('attentioncircle', AttentionCircleViewSet)

urlpatterns = router.urls
