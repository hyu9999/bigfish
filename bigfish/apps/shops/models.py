import os

from bigfish.apps.shops.apps import MEDIA_PREFIX
from bigfish.base.models import AbsTitleBase


def media_path(instance, filename):
    if isinstance(instance, Shop):
        path = os.path.join(MEDIA_PREFIX, 'shop', filename)
    else:
        path = os.path.join(MEDIA_PREFIX, 'unknown', filename)
    return path


class Shop(AbsTitleBase):
    class Meta:
        verbose_name = "商店"
        verbose_name_plural = verbose_name


class ShopRule(AbsTitleBase):
    class Meta:
        verbose_name = "商店配置规则"
        verbose_name_plural = verbose_name


class Goods(AbsTitleBase):
    class Meta:
        verbose_name = "商品"
        verbose_name_plural = verbose_name


class GoodsRule(AbsTitleBase):
    class Meta:
        verbose_name = "商品规则"
        verbose_name_plural = verbose_name


class ShopGoods(AbsTitleBase):
    class Meta:
        verbose_name = "商店商品信息"
        verbose_name_plural = verbose_name


class GoodsTradingReport(AbsTitleBase):
    class Meta:
        verbose_name = "商店商品交易记录"
        verbose_name_plural = verbose_name


class ShopGoodsReport(AbsTitleBase):
    class Meta:
        verbose_name = "商店商品交易记录"
        verbose_name_plural = verbose_name


class Marketing(AbsTitleBase):
    class Meta:
        verbose_name = "营销活动"
        verbose_name_plural = verbose_name


class MarketingRule(AbsTitleBase):
    class Meta:
        verbose_name = "营销活动规则"
        verbose_name_plural = verbose_name
