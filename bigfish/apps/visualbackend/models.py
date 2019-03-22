from django.db import models

from bigfish.apps.schools.models import Term, SchoolTerm
from bigfish.apps.visualbackend.abs_models import AbsUserBelong, AbsModel, AbsProvince, AbsCity, AbsDistrict, \
    AbsSchool, AbsKlass
from bigfish.base.choices import SCORE_TYPE


class StudentData(AbsSchool, AbsKlass, AbsUserBelong):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    school_term = models.ForeignKey(SchoolTerm,
                                    on_delete=models.CASCADE,
                                    verbose_name="学校学期",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_school_term")
    """
    完成的活动
    1."检测与复习"下的所有活动的练习数据
    2.期中考试成绩——需要手动录入，需要确定录入字段
    3.期末考试成绩——需要手动录入，需要确定录入字段
    """
    score = models.FloatField("平均成绩", default=0.0)
    """
    完成的活动
    除"检测与复习"以外的练习活动数据
    """
    right_rate = models.FloatField("平均正确率", default=0.0)
    """
    1.学习活动数据
    2.练习活动数据
    3.1V1对战数据
    以上数据中的总用时累加
    """
    use_duration = models.IntegerField("使用时长", default=0.0)  # 秒
    """
    练习活动产生的数据
    """
    exercise_num = models.IntegerField("练习题数", default=0)
    """
    1.学习活动数据 交互次数
    2.练习活动数据 答题条数
    3.1V1对战数据 答题条数
    以上数据中的条数累加
    """
    interactive_num = models.IntegerField("交互次数", default=0)
    """
    学习活动交互次数累加
    """
    man_machine_num = models.IntegerField("人机对话量", default=0)
    activity_num = models.IntegerField("活动数量", default=0)

    class Meta:
        verbose_name = "学生数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.term.title, self.username)


class TeacherData(AbsSchool, AbsKlass, AbsUserBelong):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    school_term = models.ForeignKey(SchoolTerm,
                                    on_delete=models.CASCADE,
                                    verbose_name="学校学期",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_school_term")
    """
    根据教师端统计的交互时间轴进行统计
    这个时间轴的开始时间到结尾时间之间的时间差则为一次教师端使用的总用时
    """
    use_duration = models.IntegerField("使用时长", default=0.0)  # 秒
    task_num = models.IntegerField("发布任务数", default=0.0)
    """
    教师发出的任务ID: 根据任务ID统计任务中统计的活动数量
    """
    push_activity_num = models.IntegerField("发布活动量", default=0.0)
    """
    筛选出这个老师在任务中发布过的最大Unit-Lesson值，通过这个值算出这个老师自己的教学进度百分比
    """
    teaching_progress = models.FloatField("教学进度", default=0.0)

    class Meta:
        verbose_name = "教师数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.term.title, self.username)


class StageScore(AbsProvince, AbsCity, AbsDistrict, AbsSchool, AbsKlass):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    school_term = models.ForeignKey(SchoolTerm,
                                    on_delete=models.CASCADE,
                                    verbose_name="学校学期",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_school_term")
    username = models.CharField("账户", max_length=200, blank=True, default="")
    score_type = models.IntegerField("成绩类型", choices=SCORE_TYPE, default=1)
    score = models.FloatField("成绩", blank=True, default=0.0)

    class Meta:
        verbose_name = "阶段成绩"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}-{} {}".format(self.term.title, self.klass_name, self.username, self.get_score_type_display())


class ExaminationCondition(AbsProvince, AbsCity, AbsDistrict, AbsSchool, AbsKlass):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    school_term = models.ForeignKey(SchoolTerm,
                                    on_delete=models.CASCADE,
                                    verbose_name="学校学期",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_school_term")
    score_type = models.IntegerField("成绩类型", choices=SCORE_TYPE, default=1)
    order = models.PositiveIntegerField("题目序号", blank=True, default=0)
    question = models.CharField("题目", max_length=200, blank=True, default="")
    difficult = models.FloatField("难度系数", blank=True, default=0)

    class Meta:
        verbose_name = "试卷情况"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{} {}".format(self.term.title, self.klass_name, self.get_score_type_display())
