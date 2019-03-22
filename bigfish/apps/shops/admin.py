from django.contrib import admin

from bigfish.apps.shops.models import Shop, ShopRule, GoodsRule, ShopGoods, Goods, GoodsTradingReport, ShopGoodsReport, \
    Marketing, MarketingRule
from bigfish.utils.functions import format_admin_list


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Shop)


@admin.register(ShopRule)
class ShopRuleAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ShopRule)


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Goods)


@admin.register(GoodsRule)
class GoodsRuleAdmin(admin.ModelAdmin):
    list_display = format_admin_list(GoodsRule)


@admin.register(ShopGoods)
class ShopGoodsAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ShopGoods)


@admin.register(GoodsTradingReport)
class GoodsTradingReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(GoodsTradingReport)


@admin.register(ShopGoodsReport)
class ShopGoodsReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ShopGoodsReport)


@admin.register(Marketing)
class MarketingAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Marketing)


@admin.register(MarketingRule)
class MarketingRuleAdmin(admin.ModelAdmin):
    list_display = format_admin_list(MarketingRule)
