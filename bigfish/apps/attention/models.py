import jsonfield
from django.conf import settings
from django.db import models


class AttentionCircle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    fans = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="粉丝",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_fans")
    each_other = models.BooleanField("是否相互关注", default=False)
    create_time = models.DateField("创建时间", auto_now_add=True)

    class Meta:
        unique_together = ('user', 'fans')
        verbose_name = "关注圈"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} fans".format(self.user)


class ClassmateCircle(models.Model):
    title = models.CharField("标题", max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    content = jsonfield.JSONField("发布内容", blank=True, default={})
    create_time = models.DateField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "同学圈"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)
