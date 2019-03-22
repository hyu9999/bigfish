from bigfish.apps.shops.models import Shop, ShopRule, GoodsRule, ShopGoods, Goods, GoodsTradingReport, ShopGoodsReport, \
    Marketing, MarketingRule
from bigfish.apps.shops.serializers import ShopSerializer, ShopRuleSerializer, GoodsRuleSerializer, ShopGoodsSerializer, \
    GoodsSerializer, GoodsTradingReportSerializer, ShopGoodsReportSerializer, MarketingSerializer, \
    MarketingRuleSerializer
from bigfish.base import viewsets


class ShopViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ShopRuleViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = ShopRule.objects.all()
    serializer_class = ShopRuleSerializer


class GoodsRuleViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = GoodsRule.objects.all()
    serializer_class = GoodsRuleSerializer


class ShopGoodsViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = ShopGoods.objects.all()
    serializer_class = ShopGoodsSerializer


class GoodsViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer


class GoodsTradingReportViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = GoodsTradingReport.objects.all()
    serializer_class = GoodsTradingReportSerializer


class ShopGoodsReportViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = ShopGoodsReport.objects.all()
    serializer_class = ShopGoodsReportSerializer


class MarketingViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Marketing.objects.all()
    serializer_class = MarketingSerializer


class MarketingRuleViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = MarketingRule.objects.all()
    serializer_class = MarketingRuleSerializer
