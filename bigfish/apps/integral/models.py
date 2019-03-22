from django.conf import settings
from django.db import models


class UserIntegral(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='integral',
                                verbose_name='用户',
                                primary_key=True)
    total = models.IntegerField("累计积分", default=0, blank=True)
    real = models.IntegerField("实际拥有", default=0, blank=True)

    class Meta:
        verbose_name = "用户积分"
        verbose_name_plural = verbose_name


class IntegralReport(models.Model):
    STATUS_CHOICE = (
        (1, "获得"),
        (2, "消耗"),
    )
    SCENE_CHOICE = (
        (1, "学习获得"),
        (2, "购买商品"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True, help_text="用户")
    integral = models.IntegerField("积分", default=0)
    status = models.IntegerField("状态", choices=STATUS_CHOICE, default=1)
    scene = models.IntegerField("场景", choices=SCENE_CHOICE, default=1)
    description = models.TextField("描述", default="", blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "积分流水"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.user.username, self.get_status_display())
