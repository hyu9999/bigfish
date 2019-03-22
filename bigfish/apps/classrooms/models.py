from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.apps.classrooms.abs_models import AbsActReport
from bigfish.apps.schools.models import Klass
from bigfish.apps.textbooks.models import Lesson, Activity, Unit
from bigfish.base.choices import IDENTITY_CHOICE, DELAY_STATUS, BEHAVIOR_TYPE
from bigfish.base.models import AbsQuestionRpt, AbsTitleBase, AbsRpt, AbsHis


class BlackSetting(models.Model):
    is_black = models.BooleanField("是否黑屏")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher', default=None)
    klass = models.OneToOneField(Klass, on_delete=models.CASCADE, related_name='bs_klass', default=None)

    class Meta:
        verbose_name = "1.1 黑屏"
        verbose_name_plural = verbose_name


class BlackSettingReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    klass = models.ForeignKey(Klass,
                              on_delete=models.CASCADE,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass")
    start_time = models.DateTimeField("开始时间", default=timezone.now)
    finish_time = models.DateTimeField("结束时间", default=timezone.now)

    class Meta:
        verbose_name = "1.2 黑屏记录"
        verbose_name_plural = verbose_name


class Cast(models.Model):
    is_active = models.BooleanField("是否激活", default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    klass = models.OneToOneField(Klass,
                                 on_delete=models.CASCADE,
                                 verbose_name="班级",
                                 related_name="%(app_label)s_%(class)s_klass")
    start_time = models.DateTimeField("开始时间", default=timezone.now)
    finish_time = models.DateTimeField("结束时间", default=timezone.now)

    class Meta:
        verbose_name = "2.1 投屏"
        verbose_name_plural = verbose_name


class CastReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    klass = models.ForeignKey(Klass,
                              on_delete=models.CASCADE,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass")
    start_time = models.DateTimeField("开始时间", default=timezone.now)
    finish_time = models.DateTimeField("结束时间", default=timezone.now)

    class Meta:
        verbose_name = "2.2 投屏记录"
        verbose_name_plural = verbose_name


class Classroom(AbsTitleBase, AbsRpt):
    record_date = models.DateField("记录时间", default=timezone.now)
    # 1堂课的默认时长为40分钟
    identity = models.IntegerField("角色", choices=IDENTITY_CHOICE, default=1)
    opener = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name="开启者",
                               on_delete=models.CASCADE,
                               related_name="%(app_label)s_%(class)s_opener",
                               help_text="开启者")
    klass = models.ForeignKey(Klass,
                              verbose_name="班级",
                              on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_klass",
                              help_text="班级")
    # 记录课堂使用的课程列表
    lesson = models.ManyToManyField(Lesson,
                                    verbose_name="完成课程",
                                    related_name="%(app_label)s_%(class)s_m_lesson",
                                    blank=True,
                                    help_text="完成课程")
    # 记录进行中/完成的课程
    latest_lesson = models.ForeignKey(Lesson,
                                      verbose_name="最新课程",
                                      on_delete=models.CASCADE,
                                      related_name="%(app_label)s_%(class)s_lesson",
                                      blank=True, null=True,
                                      help_text="最新课程")
    # 记录最新完成的活动
    latest_act = models.ForeignKey(Activity,
                                   verbose_name="最新活动",
                                   on_delete=models.CASCADE,
                                   related_name="%(app_label)s_%(class)s_activity",
                                   blank=True, null=True,
                                   help_text="最新活动")
    real_finish_time = models.DateTimeField("实际结束时间", default=timezone.now)
    delay_status = models.IntegerField("拖堂情况", choices=DELAY_STATUS, default=0)
    effect_time = models.FloatField("有效使用时长", blank=True, default=0)
    is_prepare = models.BooleanField("是否备课", default=False)  # 教师分为上课和备课
    is_open = models.BooleanField("是否开启", default=False)  # 上课状态

    class Meta:
        verbose_name = "3 课堂"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}][{}]{}".format(self.klass, self.opener, self.create_time)


class StuActivity(AbsActReport):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name="老师",
                                related_name="%(app_label)s_%(class)s_teacher",
                                help_text="老师")
    progress = models.FloatField("当前进度", default=0)
    max_score = models.FloatField("最大成绩", blank=True, default=0)
    avg_score = models.FloatField("平均成绩", blank=True, default=0)
    latest_score = models.FloatField("最新成绩", blank=True, default=0)
    entry_times = models.IntegerField("进入次数", default=0)
    is_finish = models.BooleanField("是否结束", default=False)

    class Meta:
        unique_together = ("classroom", "user", "activity")
        verbose_name = "4 课堂学生完成活动情况"
        verbose_name_plural = verbose_name


class ActivityReport(AbsActReport, AbsHis):
    class Meta:
        verbose_name = "5 活动记录"
        verbose_name_plural = verbose_name


class ActivityDetailReport(AbsActReport, AbsQuestionRpt, AbsHis):
    activity_report = models.ForeignKey(ActivityReport,
                                        verbose_name="活动记录",
                                        on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name="%(app_label)s_%(class)s_activity_report",
                                        help_text="活动记录")

    class Meta:
        verbose_name = '6 活动详情记录'
        verbose_name_plural = verbose_name
