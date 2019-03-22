from rest_framework import routers

from bigfish.apps.resources.views import AmazonViewSet, VideoViewSet, AudioViewSet, ImageViewSet, AnimationViewSet, \
    SpecialEffectViewSet, ImageTypeViewSet, \
    PetViewSet, LocResInfoViewSet

router = routers.SimpleRouter()
router.register('video', VideoViewSet)
router.register('audio', AudioViewSet)
router.register('image_type', ImageTypeViewSet)
router.register('image', ImageViewSet)
router.register('animation', AnimationViewSet)
router.register('special_effect', SpecialEffectViewSet)
router.register('pet', PetViewSet)
router.register('amazon', AmazonViewSet)
router.register('loc_res', LocResInfoViewSet)

urlpatterns = router.urls