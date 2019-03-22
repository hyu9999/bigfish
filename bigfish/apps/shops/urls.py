from rest_framework import routers

from bigfish.apps.shops.views import ShopViewSet, ShopRuleViewSet, GoodsRuleViewSet, ShopGoodsViewSet, GoodsViewSet, \
    GoodsTradingReportViewSet, ShopGoodsReportViewSet, MarketingViewSet, MarketingRuleViewSet

router = routers.SimpleRouter()
router.register(r'shop', ShopViewSet)
router.register(r'shoprule', ShopRuleViewSet)
router.register(r'goodsrule', GoodsRuleViewSet)
router.register(r'shopgoods', ShopGoodsViewSet)
router.register(r'goods', GoodsViewSet)
router.register(r'goodstrading_report', GoodsTradingReportViewSet)
router.register(r'shopgoods_report', ShopGoodsReportViewSet)
router.register(r'marketing', MarketingViewSet)
router.register(r'marketingrule', MarketingRuleViewSet)
urlpatterns = router.urls
