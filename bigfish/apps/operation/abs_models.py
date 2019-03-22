from django.conf import settings
from django.db import models

from bigfish.apps.textbooks.models import Unit, Lesson
from bigfish.base.choices import IDENTITY_CHOICE
from bigfish.base.const import TEACHER
from bigfish.base.models import AbsPublishRpt, AbsPersonalRpt, AbsRpt


class AbsOperateReport(AbsPublishRpt, AbsPersonalRpt, AbsRpt):
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
    identity = models.IntegerField("角色", choices=IDENTITY_CHOICE, default=TEACHER)
    unit = models.ForeignKey(Unit, verbose_name="单元", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_unit",
                             blank=True, null=True, help_text="单元")
    lesson = models.ForeignKey(Lesson, verbose_name="课程", on_delete=models.CASCADE,
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True, help_text="课程")
    scene = models.IntegerField("使用场景", choices=scene_type_choices, default=0)
    is_finish = models.BooleanField("是否结束", default=False)

    class Meta:
        abstract = True
