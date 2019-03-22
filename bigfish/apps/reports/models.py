import jsonfield
from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.apps.schools.models import Klass, School
from bigfish.apps.textbooks.models import ActType
from bigfish.base.choices import TERM_CHOICE, LEVEL_CHOICE, SCHEDULE_CHOICE, FIRST_TYPE_CHOICE

REPORTS_MEDIA_PREFIX = 'reports'


class ExaminationReport(models.Model):
    school_code = models.CharField("学校编码", max_length=20, default="")
    grade = models.CharField("班级", max_length=50, default="")
    username = models.CharField("账号", max_length=150, blank=True)
    realname = models.CharField("姓名", max_length=40, blank=True)
    exam_type = models.CharField("成绩类型", max_length=40, blank=True)
    score = models.FloatField("成绩", default=0)
    term = models.CharField("学期", max_length=40, choices=TERM_CHOICE, default=1)
    academic_year = models.IntegerField("学年", default=timezone.now().year)

    class Meta:
        unique_together = ('school_code', 'grade', 'username', 'exam_type', 'term', 'academic_year')

    def __str__(self):
        return '{} {} {}'.format(self.username, self.exam_type, self.score)


class RatingReport(models.Model):
    school_code = models.CharField("学校编码", max_length=20, default="")
    grade = models.CharField("班级", max_length=50, default="")
    term = models.IntegerField("学期", choices=TERM_CHOICE, default=1)
    academic_year = models.IntegerField("学年", default=timezone.now().year)
    username = models.CharField("账号", max_length=150, blank=True)
    realname = models.CharField("姓名", max_length=40, blank=True)
    score = models.FloatField("分数", default=0.0)
    level = models.IntegerField("评级", choices=LEVEL_CHOICE, default=1)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        unique_together = ('school_code', 'grade', 'academic_year', 'term', 'username',)

    def __str__(self):
        return '{} {} {} {}'.format(self.academic_year, self.term, self.username, self.level)


class PracticalCourseRecord(models.Model):
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                verbose_name="老师",
                                related_name="%(app_label)s_%(class)s_user")
    subject = models.CharField("科目", max_length=100, default="英语")
    schedule = models.IntegerField("课程", choices=SCHEDULE_CHOICE, default=1)
    time_range = jsonfield.JSONField("上课时间", blank=True, null=True, default={})
    teaching_date = models.DateField("教学日期", default=timezone.now)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "实际教学记录"


class AbsDailyData(models.Model):
    score = models.BigIntegerField("总分数", default=0)
    complete_num = models.IntegerField("完成次数", default=0)
    duration = models.BigIntegerField("总时长", default=0)  # 秒
    num = models.IntegerField("活动个数", default=0)
    record_date = models.DateField("记录日期", default=timezone.now)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        abstract = True


class StudentDailyData(AbsDailyData):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                verbose_name="学生",
                                related_name="%(app_label)s_%(class)s_user")

    class Meta:
        verbose_name_plural = "学生每日活动数据记录"


class KlassDailyData(AbsDailyData):
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass")
    max_ul = models.IntegerField("最大课程数", default=0)
    total_ul = models.IntegerField("总课程数", default=0)
    avg_ul = models.IntegerField("平均学习进度", default=0)
    use_duration = models.BigIntegerField("使用pad时长", default=0)
    course_num = models.IntegerField("课程数", default=0)

    class Meta:
        verbose_name_plural = "班级每日活动数据记录"


class SchoolDailyData(AbsDailyData):
    school = models.ForeignKey(School, on_delete=models.CASCADE,
                               verbose_name="学校",
                               related_name="%(app_label)s_%(class)s_school")
    avg_ul = models.IntegerField("平均学习进度", default=0)
    use_duration = models.BigIntegerField("使用pad时长", default=0)
    course_num = models.IntegerField("课程数", default=0)

    class Meta:
        verbose_name_plural = "学校每日活动数据记录"


class ActivityDailyData(models.Model):
    school_id = models.IntegerField("学校ID", blank=True)
    school_name = models.CharField("学校名称", max_length=500)
    klass_id = models.IntegerField("班级ID", blank=True)
    klass_name = models.CharField("班级名称", max_length=500)
    study_type = models.IntegerField("活动分类", choices=FIRST_TYPE_CHOICE, default=1)
    act_type_id = models.IntegerField("活动类型ID", blank=True)
    act_type_name = models.CharField("二级分类", max_length=250)
    record_date = models.DateField("记录日期", default=timezone.now)
    score = models.BigIntegerField("总分数", default=0)
    complete_num = models.IntegerField("完成次数", default=0)
    num = models.IntegerField("参与次数", default=0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "活动每日数据记录"
