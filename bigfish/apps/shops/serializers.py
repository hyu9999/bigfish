from rest_framework import serializers

from bigfish.apps.shops.models import Shop, ShopRule, GoodsRule, ShopGoods, Goods, GoodsTradingReport, ShopGoodsReport, \
    Marketing, MarketingRule


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class ShopRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopRule
        fields = '__all__'


class GoodsRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsRule
        fields = '__all__'


class ShopGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopGoods
        fields = '__all__'


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'


class GoodsTradingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsTradingReport
        fields = '__all__'


class ShopGoodsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopGoodsReport
        fields = '__all__'


class MarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketing
        fields = '__all__'


class MarketingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingRule
        fields = '__all__'
