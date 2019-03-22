from django.conf.urls import url
from rest_framework import routers

from bigfish.apps.dubbing.views import DubbingSRCViewSet, UserDubbingViewSet, DubbingZanViewSet, wx_share_view, \
    DubbingCategoryViewSet, DubbingMainViewSet, DubbingClickViewSet, \
    SubCompetitionViewSet, CompetitionViewSet, CompetitionRankViewSet, RewardConfigViewSet

router = routers.SimpleRouter()

router.register('dubbing_main', DubbingMainViewSet)
router.register('dubbing_category', DubbingCategoryViewSet)
router.register('dubbingsrc', DubbingSRCViewSet)
router.register('userdubbing', UserDubbingViewSet)
router.register('dubbing_click', DubbingClickViewSet)
router.register('dubbingZan', DubbingZanViewSet)
router.register('competition', CompetitionViewSet)
router.register('sub_competition', SubCompetitionViewSet)
router.register('competition_rank', CompetitionRankViewSet)
router.register('reward_config', RewardConfigViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^share/$', wx_share_view)
]
