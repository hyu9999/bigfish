from rest_framework import routers

from bigfish.apps.textbooks.views import UnitViewSet, TextbookViewSet, LessonViewSet, ActTabViewSet, ActivityViewSet, \
    PublishVersionViewSet, ActTypeViewSet, PrepareAdviseViewSet, LessonDescriptionViewSet

router = routers.SimpleRouter()
router.register(r'publishversion', PublishVersionViewSet)
router.register(r'textbook', TextbookViewSet)
router.register(r'unit', UnitViewSet)
router.register(r'lesson', LessonViewSet)
router.register(r'act_tab', ActTabViewSet)
router.register(r'act_type', ActTypeViewSet)
router.register(r'activity', ActivityViewSet)
router.register(r'prepare_advise', PrepareAdviseViewSet)
router.register(r'lesson_description', LessonDescriptionViewSet)
urlpatterns = router.urls