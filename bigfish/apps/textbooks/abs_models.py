from django.db import models

media_path = None


class AbsTextbooks(models.Model):
    title = models.CharField("名称", max_length=250)
    en_title = models.CharField("英语名", max_length=250, blank=True, default="")
    subtitle = models.CharField("子标题", max_length=250, blank=True, default='')
    en_subtitle = models.CharField("英文子标题", max_length=250, blank=True, default="")
    short_name = models.CharField("缩略名", max_length=250, blank=True, default="")
    order = models.PositiveIntegerField("序号", blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}".format(self.title)
