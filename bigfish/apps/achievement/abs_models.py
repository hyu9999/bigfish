from django.db import models

from bigfish.apps.resources.models import Image


class AbsAchievement(models.Model):
    title = models.CharField("名称", max_length=250, blank=True, default="")
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")

    class Meta:
        abstract = True
