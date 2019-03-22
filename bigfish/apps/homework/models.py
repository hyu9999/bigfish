import jsonfield
from django.conf import settings
from django.db import models

from bigfish.apps.classrooms.abs_models import AbsHomeworkReport
from bigfish.apps.schools.models import Klass, SchoolTerm
from bigfish.base.choices import GRADE_CHOICE
from bigfish.base.models import AbsTitleBase, AbsQuestionRpt, AbsClick


class Homework(AbsTitleBase):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="创建者",
                             related_name="%(app_label)s_%(class)s_user")
    content = jsonfield.JSONField("题目列表", default={})
    push_num = models.PositiveIntegerField("推送次数", default=0, blank=True)
    integral = models.FloatField("积分", default=0.0, blank=True)
    score_rule = jsonfield.JSONField('学分规则', default={}, blank=True)
    term = models.ForeignKey(SchoolTerm,
                             on_delete=models.CASCADE,
                             verbose_name="学校学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name_plural = '1.作业'
        ordering = ['title', 'user_id', 'create_time']


class PushRecord(AbsTitleBase):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="推送人",
                             related_name="%(app_label)s_%(class)s_user")
    homework = models.ForeignKey(Homework,
                                 on_delete=models.CASCADE,
                                 verbose_name="作业",
                                 related_name="%(app_label)s_%(class)s_homework",
                                 blank=True, null=True)
    grade = models.CharField("年级", choices=GRADE_CHOICE, max_length=50)
    klass = models.ForeignKey(Klass,
                              verbose_name="推送班级",
                              related_name="%(app_label)s_%(class)s_klass")

    class Meta:
        verbose_name_plural = '2.作业推送记录'
        ordering = ['homework', 'user', 'create_time']

    def __str__(self):
        return '{}-{}'.format(self.homework.title, self.id)


class ReceiveRecord(AbsTitleBase):
    push_record = models.ForeignKey(PushRecord,
                                    on_delete=models.CASCADE,
                                    verbose_name="推送作业",
                                    related_name="%(app_label)s_%(class)s_push_record", default=0)

    question_data = jsonfield.JSONField("题目列表", default={})
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="接收人",
                             related_name="%(app_label)s_%(class)s_user")
    scores = models.FloatField("总成绩", default=0.0)
    is_read = models.BooleanField("是否已读", default=False)
    total_times = models.IntegerField("完成次数", default=0)

    class Meta:
        verbose_name_plural = '2.作业接收记录'

    def __str__(self):
        return '[{}-{}]{}'.format(self.push_record.homework.title, self.push_record.id, self.user_id)


class HomeworkRecord(AbsHomeworkReport):
    term = models.ForeignKey(SchoolTerm,
                             on_delete=models.CASCADE,
                             verbose_name="学校学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    homework = models.ForeignKey(Homework,
                                 on_delete=models.CASCADE,
                                 verbose_name="作业",
                                 related_name="%(app_label)s_%(class)s_homework",
                                 blank=True, null=True)
    push_record = models.ForeignKey(PushRecord,
                                    on_delete=models.CASCADE,
                                    verbose_name="推送作业",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_push_record")
    receive_record = models.ForeignKey(ReceiveRecord,
                                       on_delete=models.CASCADE,
                                       verbose_name="学生作业",
                                       blank=True, null=True,
                                       related_name="%(app_label)s_%(class)s_receive_record")

    class Meta:
        verbose_name_plural = '4.学生完成作业记录'

    def __str__(self):
        return "[{}]{}".format(self.push_record.__str__(), self.id)


class HomeworkDetailRecord(AbsHomeworkReport, AbsQuestionRpt):
    term = models.ForeignKey(SchoolTerm,
                             on_delete=models.CASCADE,
                             verbose_name="学校学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    homework = models.ForeignKey(Homework,
                                 on_delete=models.CASCADE,
                                 verbose_name="作业",
                                 related_name="%(app_label)s_%(class)s_homework",
                                 blank=True, null=True)
    push_record = models.ForeignKey(PushRecord,
                                    on_delete=models.CASCADE,
                                    verbose_name="推送作业",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_push_record")
    receive_record = models.ForeignKey(ReceiveRecord,
                                       on_delete=models.CASCADE,
                                       verbose_name="学生作业",
                                       blank=True, null=True,
                                       related_name="%(app_label)s_%(class)s_receive_record")

    class Meta:
        verbose_name_plural = '5.学生完成作业详情'


class HomeworkClick(AbsClick):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_用户")
    homework = models.ForeignKey(Homework,
                                 on_delete=models.CASCADE,
                                 verbose_name="作业",
                                 related_name="%(app_label)s_%(class)s_homework",
                                 blank=True, null=True)

    class Meta:
        verbose_name_plural = '作业点击记录'

    def __str__(self):
        return "{} [{}]".format(self.homework.description, self.user.username)
