import uuid

from django.db import models

from bigfish.apps.textbooks.models import Unit
from bigfish.base.choices import PART_OF_SPEECH


class KnowledgePoint(models.Model):
    coding = models.UUIDField("编码", primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    compatible_id = models.TextField('共容ID', blank=True, default="")
    title = models.CharField("名称", max_length=200)
    en_title = models.CharField("英文名称", max_length=200)
    part_of_speech = models.IntegerField("词性", choices=PART_OF_SPEECH, default=0)
    root = models.CharField("根节点名称", max_length=200, blank=True, default="")
    level = models.IntegerField("层级", blank=True, default=0)
    order = models.IntegerField("排序", blank=True, default=0)
    parent_code = models.UUIDField("父编码", default=None, null=True, blank=True)
    has_children = models.BooleanField("是否包含子节点", default=False)
    curriculum_standard = models.BooleanField("是否课标", default=False)
    desc = models.TextField("描述", blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)
    update_user = models.CharField("添加人账号", max_length=200, blank=True, default="")

    class Meta:
        verbose_name = "知识点"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
