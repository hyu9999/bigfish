import jsonfield
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bigfish.base.models import AbsTitleBase


class Public(models.Model):
    title = models.CharField(_("title"), max_length=500, unique=True)
    content = jsonfield.JSONField(_("JSON"), blank=True, null=True, default={})
    add_time = models.DateTimeField(_("add time"), blank=True, null=True)
    add_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='add_user', verbose_name=_('add user'),
                                 blank=True, null=True)
    note1 = models.TextField(_("note1"), blank=True, null=True)
    note2 = models.TextField(_("note2"), blank=True, null=True)
    note3 = models.TextField(_("note3"), blank=True, null=True)
    note4 = models.TextField(_("note4"), blank=True, null=True)
    note5 = models.TextField(_("note5"), blank=True, null=True)

    class Meta:
        verbose_name = "公共信息表"
        verbose_name_plural = verbose_name


class ATGroup(AbsTitleBase):
    class Meta:
        verbose_name = "数据表分组"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)


class AppTable(AbsTitleBase):
    app_name = models.CharField("app名称", max_length=100)
    app_verbose_name = models.CharField("app别名", max_length=100)
    table_name = models.CharField("表名", max_length=100)
    table_verbose_name = models.CharField("表别名", max_length=100)
    at_group = models.ForeignKey(ATGroup,
                                 on_delete=models.CASCADE,
                                 verbose_name="分组",
                                 blank=True, null=True,
                                 related_name="%(app_label)s_%(class)s_atgroup")
    # ["a", "b", "c"]
    is_all = models.BooleanField("是否使用全部字段", default=False)
    field_list = jsonfield.JSONField("字段列表", blank=True, null=True, default={})

    class Meta:
        verbose_name = "数据表信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.title:
            return "{}".format(self.title)
        else:
            return "{}{}".format(self.app_name, self.table_name)
