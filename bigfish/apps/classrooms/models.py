from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.apps.classrooms.abs_models import AbsActReport
from bigfish.apps.schools.models import Klass
from bigfish.apps.textbooks.models import Lesson, Activity, Unit
from bigfish.base.choices import IDENTITY_CHOICE, DELAY_STATUS, BEHAVIOR_TYPE, STU_CLASSROOM_STATUS
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
                                    blank=True, through='ClassroomLessonRelationship',
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


class OnlineReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='%(app_label)s_%(class)s_user',
                             verbose_name='用户')
    classroom = models.ForeignKey('Classroom',
                                  verbose_name="课堂",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  help_text="课堂")
    recorder = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='%(app_label)s_%(class)s_recorder',
                                 verbose_name='记录人')
    status = models.IntegerField("状态", choices=STU_CLASSROOM_STATUS, default=0)
    login_time = models.DateTimeField('上线时间', default=timezone.now)
    logout_time = models.DateTimeField('下线时间', default=timezone.now)
    online_time = models.BigIntegerField('在线时长', blank=True, default=0)

    class Meta:
        verbose_name = "3.1 在线情况记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class ClassroomLessonRelationship(models.Model):
    classroom = models.ForeignKey('Classroom',
                                  verbose_name="课堂",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  help_text="课堂")
    # 记录进行中/完成的课程
    lesson = models.ForeignKey(Lesson,
                               verbose_name="最新课程",
                               on_delete=models.CASCADE,
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True,
                               help_text="最新课程")
    is_must = models.BooleanField("是否必学", default=False)
    is_recommend = models.BooleanField("是否推荐", default=False)
    # 记录最新完成的活动
    activity = models.ForeignKey(Activity,
                                 verbose_name="活动",
                                 on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True,
                                 help_text="活动")
    activity_name = models.CharField("活动名称", max_length=200, default="")
    """
    完成比计算规则
        这堂课一共有多少正常上课的学生数记作A
        有多少已经完成该活动的学生数记作B
            A 完成活动的判定需要配合强制引导
            B 学生端的强制引导完成，则认为学生完成该活动
        B/A*100%=进度条需要进行展示填充的完成比
        文本展示格式为：B/A
    """
    completion_ratio = models.CharField("完成比", max_length=200, default="")
    has_score = models.BooleanField("是否有成绩", default=False)
    """
    平均成绩计算规则
        这堂课该活动产生了多少条已完成的练习数据记作A
        将所有数据中的成绩累加，再除以A得到平均成绩
        平均成绩只展示整数部分，小数部分直接舍去
        A   数据库记录中保留小数点后2位
    """
    avg_score = models.FloatField("平均成绩", blank=True, default=0)
    use_duration = models.FloatField("使用时长", blank=True, default=0)  # pad使用时长
    use_duration_rate = models.FloatField("使用时长占比", blank=True, default=0)  # pad使用时长占比

    class Meta:
        verbose_name = "3.2 课堂课程"
        verbose_name_plural = verbose_name


class StuActivity(AbsActReport):
    """
    记录课堂内学生完成活动情况，单个学生一堂课只会记录一次活动

    activity_name = models.CharField("活动名称", max_length=200, default="")
    activity_icon = models.ForeignKey(Image,
                              verbose_name="活动图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")

    """
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name="老师",
                                related_name="%(app_label)s_%(class)s_teacher",
                                help_text="老师")
    progress = models.FloatField("当前进度", default=0)
    max_score = models.FloatField("最大成绩", blank=True, default=0)
    avg_score = models.FloatField("平均成绩", blank=True, default=0)
    latest_score = models.FloatField("最新成绩", blank=True, default=0)
    entry_times = models.IntegerField("进入次数", default=0)
    is_finish = models.BooleanField("是否发布结束", default=False)

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
