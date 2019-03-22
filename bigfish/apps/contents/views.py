from bigfish.base import viewsets
from rest_framework.parsers import JSONParser, MultiPartParser

from bigfish.apps.contents.models import Article, \
    Sentence, WordType, TextbookWord
from bigfish.apps.contents.serializers import ArticleSerializer, SentenceSerializer, WordTypeSerializer, \
    TextbookWordSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    parser_classes = (JSONParser, MultiPartParser)


class SentenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    parser_classes = (JSONParser, MultiPartParser)


class WordTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WordType.objects.all()
    serializer_class = WordTypeSerializer
    parser_classes = (JSONParser, MultiPartParser)


class TextbookWordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TextbookWord.objects.all()
    serializer_class = TextbookWordSerializer
    parser_classes = (JSONParser, MultiPartParser)
