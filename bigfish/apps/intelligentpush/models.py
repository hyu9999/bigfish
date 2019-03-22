from django.db import models

from bigfish.base.choices import PUSH_TYPE_CHOICE
from bigfish.base.models import AbsPublishRpt, AbsPersonalRpt, AbsActRpt


class IntelligentPush(AbsPublishRpt, AbsPersonalRpt, AbsActRpt):
    push_user = models.IntegerField("推送者ID", blank=True, default=0)
    is_homework = models.BooleanField("是否作业", default=False)
    push_type = models.IntegerField("推送类型", choices=PUSH_TYPE_CHOICE, default=1, db_index=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "智能推送记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.username, self.get_push_type_display())


class PushQuestions(AbsPublishRpt, AbsPersonalRpt, AbsActRpt):
    intelligent_push = models.ForeignKey(IntelligentPush,
                                         on_delete=models.CASCADE,
                                         verbose_name="智能推送",
                                         related_name="%(app_label)s_%(class)s_intelligent_push")
    push_user = models.IntegerField("推送者ID", blank=True, default=0)
    is_homework = models.BooleanField("是否作业", default=False)
    push_type = models.IntegerField("推送类型", choices=PUSH_TYPE_CHOICE, default=1, db_index=True)
    question_id = models.IntegerField("题目", blank=True, default=0)
    question_content = models.TextField("题目内容", blank=True, default=0)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "智能推送题目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}-{}".format(self.username, self.get_push_type_display(), self.question_content)
