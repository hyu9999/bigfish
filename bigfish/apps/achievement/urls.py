from rest_framework import routers

from bigfish.apps.achievement.views import AchievementViewSet, UserAchievementViewSet

router = routers.SimpleRouter()

router.register('achievement', AchievementViewSet)
router.register('userachievement', UserAchievementViewSet)

urlpatterns = router.urls
