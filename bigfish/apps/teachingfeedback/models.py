from django.db import models

from bigfish.apps.schools.models import Term
from bigfish.apps.teachingfeedback.abs_models import AbsData, AbsAppraisalData
from bigfish.apps.visualbackend.abs_models import AbsDistrict, AbsSchool, AbsKlass, AbsUnit, AbsLesson


class UnitData(AbsDistrict, AbsSchool, AbsKlass, AbsUnit, AbsData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    teacher_id = models.IntegerField("教师ID", blank=True, default=0)
    username = models.CharField("教师账号", max_length=200, blank=True, default="")
    teach_advice = models.TextField("教学建议", blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "单元数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}{}{}]{}".format(self.short_name, self.grade_name, self.klass_name, self.unit_title)


class UnitTestData(AbsDistrict, AbsSchool, AbsKlass, AbsUnit):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    teacher_id = models.IntegerField("教师ID", blank=True, default=0)
    username = models.CharField("教师账号", max_length=200, blank=True, default="")
    # 单元测试成绩
    score = models.FloatField("平均成绩", blank=True, default=0.0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "单元测试数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}{}{}]{}".format(self.short_name, self.grade_name, self.klass_name, self.unit_title)


class TestReview(AbsDistrict, AbsSchool, AbsKlass, AbsData):
    # 单元检测、期中模拟、单元复习、综合复习
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    lesson_title = models.CharField("课程名称", max_length=200, blank=True, default=0.0)
    score = models.FloatField("平均成绩", blank=True, default=0.0)
    teach_advice = models.TextField("教学建议", blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "检测与复习"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}{}{}]{}".format(self.short_name, self.grade_name, self.klass_name, self.lesson_title)


class LessonData(AbsDistrict, AbsSchool, AbsKlass, AbsUnit, AbsLesson, AbsData, AbsAppraisalData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    teacher_id = models.IntegerField("教师ID", blank=True, default=0)
    username = models.CharField("教师账号", max_length=200, blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "课程数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}{}{}]{}-{}".format(self.short_name, self.grade_name, self.klass_name, self.unit_title,
                                      self.lesson_title)


class ActivityData(AbsDistrict, AbsSchool, AbsKlass, AbsData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    activity_title = models.CharField("活动名称", max_length=200, blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "活动数据"
        verbose_name_plural = verbose_name
