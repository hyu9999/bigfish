from rest_framework import routers

from bigfish.apps.contents.views import ArticleViewSet, SentenceViewSet, WordTypeViewSet, TextbookWordViewSet

router = routers.SimpleRouter()
router.register('article', ArticleViewSet)
router.register('sentence', SentenceViewSet)
router.register('word_type', WordTypeViewSet)
router.register('textbook_word', TextbookWordViewSet)

urlpatterns = router.urls
