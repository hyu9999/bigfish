import os

import jsonfield
from django.conf import settings
from django.db import models

from bigfish.apps.classrooms.models import ActivityReport, Classroom
from bigfish.apps.textbooks.models import Activity


def media_path(instance, filename):
    if isinstance(instance, SpeechEvaluationReport):
        path = os.path.join("res", 'prores', 'se_video', filename)
    else:
        path = os.path.join("res", 'prores', 'unknown', filename)
    return path


class SpeechEvaluation(models.Model):
    """
    语音评测
    """
    title = models.CharField("名称", max_length=250, blank=True, default="")
    en_title = models.CharField("英文名称", max_length=250, blank=True, default="")
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    input = jsonfield.JSONField("入参", blank=True, default={})
    output = jsonfield.JSONField("出参", blank=True, default={})
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = '语音评测'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)


class SpeechEvaluationDetail(models.Model):
    """
    语音评测字段说明
    """
    ENTRY_EXIT = (
        (1, "出参"),
        (2, "入参"),
    )
    speech_evaluation = models.ForeignKey(SpeechEvaluation, verbose_name="语音评测", on_delete=models.CASCADE,
                                          related_name="%(app_label)s_%(class)s_speech_evaluation")
    entry_exit = models.IntegerField("出入参", choices=ENTRY_EXIT, default=1)
    name = models.CharField("名称", max_length=250, blank=True, default="")
    record_type = models.CharField("类型", max_length=250, blank=True, default="")
    is_required = models.BooleanField("是否必须", default=False)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = '语音评测字段说明'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.name)


class SpeechEvaluationReport(models.Model):
    name = models.CharField("内容", max_length=1000)
    voice_recognition = jsonfield.JSONField("语音识别", blank=True, default={})
    classroom = models.ForeignKey(Classroom, verbose_name="课堂",
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  blank=True, null=True, help_text="课堂")
    activity_report = models.ForeignKey(ActivityReport, verbose_name="活动记录", on_delete=models.CASCADE,
                                        related_name="%(app_label)s_%(class)s_activity_report",
                                        blank=True, null=True, help_text="活动记录")
    activity = models.ForeignKey(Activity, verbose_name="活动", on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True, help_text="活动")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True, help_text="用户")
    eval_type = models.ForeignKey(SpeechEvaluation, verbose_name="评测类型", on_delete=models.CASCADE,
                                  related_name="%(app_label)s_%(class)s_eval_type",
                                  help_text="评测类型")
    res = models.FileField("资源", upload_to=media_path, blank=True, null=True)
    result = jsonfield.JSONField("测评结果", blank=True, default={})
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "语音测评记录"
        verbose_name_plural = verbose_name
