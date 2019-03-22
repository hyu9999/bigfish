from django.conf.urls import url
from rest_framework import routers

from bigfish.apps.users.views import UserViewSet, UserFeedbackViewSet, UserCourseViewSet, UserKlassRelationshipViewSet, \
    UserOnlineViewSet, UserPositionViewSet, UserScenariosRopViewSet, UserRegViewSet, BigFishSessionView

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'user_klass', UserKlassRelationshipViewSet)
router.register(r'user_course', UserCourseViewSet)
router.register(r'feedback', UserFeedbackViewSet)
router.register(r'user_online', UserOnlineViewSet)
router.register(r'user_position', UserPositionViewSet)
router.register(r'user_scenarios', UserScenariosRopViewSet)
router.register(r'user_reg', UserRegViewSet)
urlpatterns = router.urls
urlpatterns += [
    url(r'^bigfish_session/$', BigFishSessionView.as_view(), name='bigfish_session'),
]
