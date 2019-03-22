import jsonfield
from django.db import models


class Area(models.Model):
    coding = models.AutoField("区划编码", primary_key=True)
    name = models.CharField("区划名称", max_length=200)
    level = models.CharField("区划级别", max_length=50)
    bbox = jsonfield.JSONField("bbox", blank=True, null=True, default=[])
    center = jsonfield.JSONField("区划中心点", blank=True, null=True, default=[])
    idealZoom = models.IntegerField("最佳缩放级别", blank=True, null=True, default=0)
    pz = models.IntegerField(blank=True, null=True, default=0)
    radix = models.IntegerField(blank=True, null=True, default=0)
    acroutes = jsonfield.JSONField("acroutes", blank=True, null=True, default=[])
    prov_code = models.IntegerField("区划编码", blank=True, null=True, default=0, db_index=True)
    city_code = models.IntegerField("市级区划编码", blank=True, null=True, default=0, db_index=True)
    is_active = models.BooleanField("是否有效", default=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # add_time = models.DateTimeField("添加时间", default=timezone.now)
    # update_time = models.DateTimeField("更新时间", default=timezone.now)

    class Meta:
        verbose_name = "区域"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.name)


class ProvinceInfo(models.Model):
    name = models.CharField('省份的名称备注', max_length=255)
    coding = models.CharField('省份对应的编码', max_length=255)

    class Meta:
        verbose_name_plural = '省级行政区编码表'
