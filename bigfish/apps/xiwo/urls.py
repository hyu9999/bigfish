from django.conf.urls import url
from rest_framework import routers

from bigfish.apps.xiwo import views
from bigfish.apps.xiwo.views import SerialBindingRelationViewSet

router = routers.SimpleRouter()
router.register(r'serial_binding_relation', SerialBindingRelationViewSet)
urlpatterns = router.urls
urlpatterns += [
    url(r'^bind_device/$', views.bind_device, name="bind_device"),
    url(r'^get_serial_info/$', views.get_serial_info, name="get_serial_info"),
]
