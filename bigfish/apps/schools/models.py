import jsonfield
from django.contrib.postgres.fields import ArrayField
from django.db import models

from bigfish.apps.areas.models import Area
from bigfish.apps.textbooks.models import PublishVersion, Lesson, Textbook, Unit, ActTab, Activity
from bigfish.base.choices import TERM_CHOICE, GRADE_CHOICE
from bigfish.base.models import AbsTitleBase, AbsPublishRpt, AbsDateRpt, AbsExtraTitle


class Term(AbsTitleBase, AbsDateRpt):
    academic_year = models.CharField("学年", max_length=10)
    term = models.IntegerField("学期", choices=TERM_CHOICE, default=1)

    class Meta:
        verbose_name = "学期"
        verbose_name_plural = verbose_name


class TermWeek(AbsTitleBase, AbsDateRpt):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name = "学周"
        verbose_name_plural = verbose_name


class Segment(AbsExtraTitle):
    coding = models.CharField("学段编码", max_length=20, default="")

    class Meta:
        verbose_name = "学段"
        verbose_name_plural = verbose_name


class School(AbsExtraTitle):
    STUDY_SECTION = (
        (1, "小学"),
        (2, "初中"),
        (3, "高中"),
    )
    coding = models.CharField("学校编码", max_length=20, default="")
    study_section = models.CharField("学段", max_length=30, blank=True)
    # 1v1 匹配机器人查询正式学校学生镜像
    is_normal = models.BooleanField("是否为正式学校", default=True)
    use_cast = models.BooleanField("是否使用投屏", default=False)
    auto_remember_pwd = models.BooleanField("自动记住密码", default=False)
    areas = models.ForeignKey(Area,
                              verbose_name="区域",
                              related_name="%(app_label)s_%(class)s_area",
                              blank=True, null=True,
                              help_text="区域")
    position = models.CharField("坐标", max_length=500, default='')
    # 新增
    hf_id = models.CharField("hf_id", max_length=200, blank=True, default="")
    school_run_type_code = models.CharField("校办型代码", max_length=200, blank=True, default="")
    post_num = models.CharField("邮编", max_length=200, blank=True, default="")
    contact_user = models.CharField("联系人", max_length=200, blank=True, default="")
    contact_mobile = models.CharField("联系电话", max_length=200, blank=True, default="")
    contact_fax_mobile = models.CharField("传真", max_length=200, blank=True, default="")
    email = models.CharField("邮箱", max_length=200, blank=True, default="")
    web_url = models.CharField("主页", max_length=200, blank=True, default="")
    sync_status = models.CharField("同步编码", max_length=200, blank=True, default="")

    class Meta:
        ordering = ('id',)
        verbose_name = "学校"
        verbose_name_plural = verbose_name


class Grade(AbsExtraTitle):
    """
    可单独同步， 可不处理
    """
    hf_id = models.CharField("hf_id", max_length=200, blank=True, default="")
    coding = models.CharField("年级编码", max_length=20, default="")
    segment_name = models.CharField("学段", max_length=20, default="")
    sync_status = models.CharField("同步编码", max_length=200, blank=True, default="")

    class Meta:
        ordering = ('id',)
        verbose_name = "年级"
        verbose_name_plural = verbose_name


class RegisterSerial(models.Model):
    school = models.ForeignKey(School,
                               on_delete=models.CASCADE,
                               verbose_name="学校",
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_school")
    serial_num = models.BigIntegerField("序列号", unique=True)
    encrypt_sn = models.CharField("加密序列", max_length=100, unique=True)
    is_active = models.BooleanField("是否有效", blank=True, default=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "注册序列号"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.serial_num)


class SchoolTerm(AbsTitleBase, AbsDateRpt):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    school = models.ForeignKey(School,
                               on_delete=models.CASCADE,
                               verbose_name="学校",
                               related_name="%(app_label)s_%(class)s_school")

    class Meta:
        verbose_name = "学校学期"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.school.title, self.title)


class SchoolWeek(AbsTitleBase, AbsDateRpt):
    term_week = models.ForeignKey(TermWeek,
                                  on_delete=models.CASCADE,
                                  verbose_name="学周",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_term_week")
    school = models.ForeignKey(School,
                               on_delete=models.CASCADE,
                               verbose_name="学校",
                               related_name="%(app_label)s_%(class)s_school")

    def __str__(self):
        return "{} {}".format(self.school.title, self.term_week.title)

    class Meta:
        verbose_name = "学校学周"
        verbose_name_plural = verbose_name


class Klass(AbsTitleBase):
    school = models.ForeignKey(School, verbose_name="学校",
                               related_name="%(app_label)s_%(class)s_school",
                               blank=True, null=True)
    grade = models.IntegerField("年级", choices=GRADE_CHOICE, default=11)
    publish = models.ForeignKey(PublishVersion, verbose_name="教材",  # 班级对应的默认教材
                                related_name="%(app_label)s_%(class)s_publish",
                                blank=True, null=True)
    # 新增字段
    hf_id = models.CharField("hf_id", max_length=200, blank=True, default="")
    segment_name = models.CharField("学段", max_length=20, default="")
    master_teacher = models.CharField("班主任", max_length=100, blank=True, default="")
    length_schooling = models.IntegerField("学制", blank=True, default=0)
    graduated_year = models.IntegerField("毕业年份", blank=True, default=0)
    entrance_year = models.IntegerField("入学年份", blank=True, default=0)
    sync_status = models.CharField("同步编码", max_length=200, blank=True, default="")

    class Meta:
        verbose_name = "班级"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.description)


class KlassActProgress(models.Model):
    klass = models.ForeignKey(Klass,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass")
    lesson = models.ForeignKey(Lesson,
                               verbose_name="课程",
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True)
    act_tab = models.ForeignKey(ActTab,
                                verbose_name="活动页签",
                                related_name="%(app_label)s_%(class)s_act_tab",
                                blank=True, null=True)
    activity = models.ForeignKey(Activity,
                                 verbose_name="活动",
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True)
    suggested_time = models.FloatField("建议时长", blank=True, default=0)
    time_duration = models.FloatField("使用时长", blank=True, default=0)
    is_finish = models.BooleanField("活动是否完成", blank=True, default=False)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "班级活动进度"
        verbose_name_plural = verbose_name
        ordering = ['act_tab__order', 'activity__order']

    def __str__(self):
        return "{}-{}".format(self.klass.title, self.lesson.title)


class KlassProgress(models.Model):
    klass = models.OneToOneField(Klass, verbose_name="班级",
                                 related_name="%(app_label)s_%(class)s_klass",
                                 primary_key=True)
    progress = models.IntegerField("授课进度", blank=True, default=0)
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    textbook = models.ForeignKey(Textbook, verbose_name="实时课程教材",
                                 related_name="%(app_label)s_%(class)s_textbook",
                                 blank=True, null=True)
    unit = models.ForeignKey(Unit,
                             verbose_name="实时单元",
                             related_name="%(app_label)s_%(class)s_unit",
                             blank=True, null=True)
    lesson = models.ForeignKey(Lesson,
                               verbose_name="实时课程",
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True)
    act_total_num = models.IntegerField("当前课程活动总数", blank=True, default=0)
    act_finish_num = models.IntegerField("完成活动数", blank=True, default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "班级进度"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "班级进度[{}-{}]".format(self.klass.title, self.progress)


class ClassSchedule(AbsTitleBase):
    SEASON_CHOICE = (
        ("1", "春季"),
        ("2", "夏季"),
        ("3", "秋季"),
        ("4", "冬季")
    )
    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_school'
    )
    season = models.CharField("季节", choices=SEASON_CHOICE, max_length=20)
    season_timestamp = ArrayField(models.DateField(), blank=True, null=True)
    schedule_data = jsonfield.JSONField("课程时间对应关系", blank=True, null=True, default={})

    class Meta:
        unique_together = ('school', 'season')
        verbose_name = "课程表"
        verbose_name_plural = verbose_name
