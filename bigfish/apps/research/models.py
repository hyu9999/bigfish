import jsonfield
from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.apps.schools.models import ClassSchedule, SchoolTerm, Klass
from bigfish.apps.visualbackend.abs_models import AbsDistrict, AbsSchool, AbsKlass
from bigfish.base.choices import WEEK_CHOICE, SCHEDULE_CHOICE, TEACHER_TYPE_CHOICE, TEACHING_MODE_CHOICE, \
    LESSON_TYPE_CHOICE, REVIEW_TYPE_CHOICE


class AbsResearch(models.Model):
    title = models.CharField("标题", max_length=250)
    subtitle = models.CharField("子标题", max_length=250, blank=True)
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.title)


class AbsReply(models.Model):
    content = models.TextField("回复内容", default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    create_time = models.DateTimeField("回复时间", auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.content)


class AbsWatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    create_time = models.DateTimeField("回复时间", auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {}'.format(self.user.username, self.create_time)


class TeacherSchedule(AbsResearch):
    class_schedule = models.ForeignKey(ClassSchedule,
                                       verbose_name="学校课程表",
                                       blank=True, null=True,
                                       related_name="%(app_label)s_%(class)s_class_schedule")
    term_schedule = models.ForeignKey(SchoolTerm,
                                      on_delete=models.CASCADE,
                                      verbose_name="学校学期",
                                      related_name="%(app_label)s_%(class)s_term_schedule")
    klass = models.ForeignKey(Klass,
                              on_delete=models.CASCADE,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                verbose_name="老师",
                                related_name="%(app_label)s_%(class)s_user")
    week = models.IntegerField("星期", choices=WEEK_CHOICE, default=1)
    schedule = models.IntegerField("课程", choices=SCHEDULE_CHOICE, default=1)
    time_range = jsonfield.JSONField("上课时间", blank=True, null=True, default={})

    class Meta:
        verbose_name_plural = "教师课程表"


class PrepareLesson(AbsResearch):
    content = jsonfield.JSONField("内容", blank=True, null=True, default={})
    teacher_schedule = models.ForeignKey(TeacherSchedule,
                                         on_delete=models.CASCADE,
                                         verbose_name="教师课程",
                                         related_name="%(app_label)s_%(class)s_teacher_schedule")
    teaching_date = models.DateField("教学日期", default=timezone.now)

    class Meta:
        verbose_name_plural = "教师备课表"


class PrepareLessonReply(AbsReply):
    prepare_lesson = models.ForeignKey(PrepareLesson,
                                       on_delete=models.CASCADE,
                                       verbose_name="教师备课",
                                       related_name="%(app_label)s_%(class)s_prepare_lesson")

    class Meta:
        verbose_name_plural = "教师备课回复信息表"


class PrepareLessonWatch(AbsWatch):
    prepare_lesson = models.ForeignKey(PrepareLesson,
                                       on_delete=models.CASCADE,
                                       verbose_name="教师备课",
                                       related_name="%(app_label)s_%(class)s_prepare_lesson")

    class Meta:
        verbose_name_plural = "教师备课查看记录表"


class TeachingLog(AbsResearch):
    teacher_type = models.IntegerField("教师类型", choices=TEACHER_TYPE_CHOICE, default=1)  # 老师填写
    mode = models.IntegerField("模式名称", choices=TEACHING_MODE_CHOICE, default=1)
    online_time = models.FloatField("线上时间", blank=True, default=0.0)
    progress = models.FloatField("课程进度", blank=True, default=0.0)
    lesson_type = models.IntegerField("课型", choices=LESSON_TYPE_CHOICE, default=1)  # 老师填写
    reflection = models.TextField("课后反思", blank=True, default="")  # 教研员手动录入
    advice = models.TextField("教学建议", blank=True, default="")  # 教研员手动录入
    content = jsonfield.JSONField("内容", blank=True, null=True, default={})
    teacher_schedule = models.ForeignKey(TeacherSchedule,
                                         on_delete=models.CASCADE,
                                         verbose_name="教师课程",
                                         related_name="%(app_label)s_%(class)s_teacher_schedule")
    teaching_date = models.DateField("教学日期", default=timezone.now)

    class Meta:
        verbose_name_plural = "教学日志表"


class TeachingLogReply(AbsReply):
    teaching_log = models.ForeignKey(TeachingLog,
                                     on_delete=models.CASCADE,
                                     verbose_name="教学日志",
                                     related_name="%(app_label)s_%(class)s_teaching_log")

    class Meta:
        verbose_name_plural = "教学日志回复信息表"


class TeachingLogWatch(AbsWatch):
    teaching_log = models.ForeignKey(TeachingLog,
                                     on_delete=models.CASCADE,
                                     verbose_name="教学日志",
                                     related_name="%(app_label)s_%(class)s_teaching_log")

    class Meta:
        verbose_name_plural = "教学日志查看记录表"


class ResearchActivity(AbsResearch):
    content = models.TextField("内容", blank=True, null=True, default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")

    class Meta:
        verbose_name_plural = "教研活动表"


class ResearchActivityReply(AbsReply):
    research_activity = models.ForeignKey(ResearchActivity,
                                          on_delete=models.CASCADE,
                                          verbose_name="教学日志",
                                          related_name="%(app_label)s_%(class)s_research_activity")

    class Meta:
        verbose_name_plural = "教研活动回复信息表"


class ResearchActivityWatch(AbsWatch):
    research_activity = models.ForeignKey(ResearchActivity,
                                          on_delete=models.CASCADE,
                                          verbose_name="教学日志",
                                          related_name="%(app_label)s_%(class)s_research_activity")

    class Meta:
        verbose_name_plural = "教研活动查看记录表"


class TeachingEffect(AbsDistrict, AbsSchool, AbsKlass):
    teaching_log = models.ForeignKey(TeachingLog,
                                     on_delete=models.CASCADE,
                                     blank=True, null=True,
                                     verbose_name="教学日志",
                                     related_name="%(app_label)s_%(class)s_teaching_log")
    activity_name = models.CharField("活动名称", max_length=200, default="")
    finish_num = models.IntegerField("完成人数", blank=True, default=0)
    total_num = models.IntegerField("总人数", blank=True, default=0)
    right_rate = models.FloatField("平均正确率", blank=True, default=0.0)
    interactive_num = models.FloatField("平均交互次数", blank=True, default=0.0)
    std_val = models.FloatField("标准差", blank=True, default=0.0)
    study_time = models.FloatField("平均学习时间", blank=True, default=0.0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "教学效果"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.activity_name)


class TeachingAchievement(AbsDistrict, AbsSchool, AbsKlass):
    teaching_log = models.ForeignKey(TeachingLog,
                                     on_delete=models.CASCADE,
                                     blank=True, null=True,
                                     verbose_name="教学日志",
                                     related_name="%(app_label)s_%(class)s_teaching_log")

    review_type = models.IntegerField("考察类型", choices=REVIEW_TYPE_CHOICE, default=1)
    target = models.TextField("教学目标", blank=True, default="")
    score = models.FloatField("评分", blank=True, default=0.0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "教学目标达成情况"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.review_type)


class TeachingAdvice(AbsDistrict, AbsSchool, AbsKlass):
    teaching_log = models.ForeignKey(TeachingLog,
                                     on_delete=models.CASCADE,
                                     blank=True, null=True,
                                     verbose_name="教学日志",
                                     related_name="%(app_label)s_%(class)s_teaching_log")

    order = models.IntegerField("序号", default=0)
    desc = models.TextField("特点", blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "教学建议"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.order, self.desc)
