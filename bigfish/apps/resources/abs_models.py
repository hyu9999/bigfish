from django.db import models

media_directory = None


class AbsSource(models.Model):
    title = models.CharField("名称", max_length=250, default="")
    en_title = models.CharField("英语名", max_length=250, default="", blank=True)
    content = models.TextField("内容", blank=True, null=True, default="")
    en_content = models.TextField("英文内容", blank=True, null=True, default="")
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.title)
