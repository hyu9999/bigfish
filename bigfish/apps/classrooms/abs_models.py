from django.conf import settings
from django.db import models

from bigfish.apps.textbooks.models import Unit, Lesson, Activity
from bigfish.base.models import AbsActDataRpt, AbsPublishRpt, AbsActRpt, AbsPersonalRpt, AbsRpt

media_directory = None


class AbsActReport(AbsActDataRpt, AbsPublishRpt, AbsActRpt, AbsPersonalRpt, AbsRpt):
    scene_type_choices = (
        (0, "unknown"),
        (1, "自助课堂"),
        (2, "课堂"),
    )
    classroom = models.ForeignKey('Classroom',
                                  verbose_name="课堂",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  help_text="课堂")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True, help_text="用户")
    unit = models.ForeignKey(Unit, verbose_name="单元", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_unit",
                             blank=True, null=True, help_text="单元")
    lesson = models.ForeignKey(Lesson, verbose_name="课程", on_delete=models.CASCADE,
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True, help_text="课程")
    activity = models.ForeignKey(Activity, verbose_name="活动", on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True, help_text="活动")
    scene = models.IntegerField("使用场景", choices=scene_type_choices, default=0)
    is_push = models.BooleanField("是否推送题", default=False)

    class Meta:
        abstract = True


class AbsHomeworkReport(AbsActDataRpt, AbsPublishRpt, AbsPersonalRpt, AbsRpt):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True, help_text="用户")
    unit = models.ForeignKey(Unit, verbose_name="单元", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_unit",
                             blank=True, null=True, help_text="单元")
    lesson = models.ForeignKey(Lesson, verbose_name="课程", on_delete=models.CASCADE,
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True, help_text="课程")
    activity = models.ForeignKey(Activity, verbose_name="活动", on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True, help_text="活动")

    class Meta:
        abstract = True
