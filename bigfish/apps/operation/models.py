from django.conf import settings
from django.db import models

from bigfish.apps.classrooms.models import Classroom
from bigfish.apps.operation.abs_models import AbsOperateReport
from bigfish.apps.textbooks.models import Lesson, Activity
from bigfish.base.models import AbsClick


class OperateType(models.Model):
    title = models.CharField("标题", max_length=250, default="")
    subtitle = models.CharField("子标题", max_length=250, blank=True, default='')
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # create_time = models.DateTimeField("创建时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    # update_time = models.DateTimeField("更新时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    class Meta:
        verbose_name = "操作类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Operation(models.Model):
    title = models.CharField("标题", max_length=250, default="")
    subtitle = models.CharField("子标题", max_length=250, blank=True, default='')
    operate_type = models.ForeignKey(OperateType,
                                     on_delete=models.CASCADE,
                                     verbose_name="操作类型",
                                     related_name="%(app_label)s_%(class)s_operate_type")
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # create_time = models.DateTimeField("创建时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    # update_time = models.DateTimeField("更新时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    class Meta:
        verbose_name = "操作"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class OperationRecord(AbsOperateReport):
    operate_type = models.ForeignKey(OperateType,
                                     on_delete=models.CASCADE,
                                     verbose_name="操作类型",
                                     related_name="%(app_label)s_%(class)s_operate_type")
    operation = models.ForeignKey(Operation,
                                  on_delete=models.CASCADE,
                                  verbose_name="操作",
                                  related_name="%(app_label)s_%(class)s_operation")
    operate_id = models.IntegerField("操作ID", blank=True, default=0)
    classroom = models.ForeignKey(Classroom,
                                  verbose_name="课堂",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  help_text="课堂")
    duration = models.FloatField("时长", blank=True, default=0)
    finish_num = models.PositiveIntegerField("完成人数", default=0)
    unfinished_num = models.PositiveIntegerField("未完成人数", default=0)
    has_score = models.BooleanField("是否产生成绩", default=False)
    avg_score = models.FloatField("平均成绩", blank=True, default=0)

    class Meta:
        verbose_name = "操作记录"
        verbose_name_plural = verbose_name


class ActClick(AbsClick):
    lesson = models.ForeignKey(Lesson, verbose_name="课程",
                               blank=True, null=True,
                               related_name='%(app_label)s_%(class)s_lesson')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="用户", default=None,
                             related_name="%(app_label)s_%(class)s_user")
    classroom = models.ForeignKey(Activity, on_delete=models.CASCADE,
                                  null=True, blank=True,
                                  verbose_name="课堂",
                                  related_name="%(app_label)s_%(class)s_user")
    """
       特殊活动 activity 记录规则：
           1v1: -1
           课堂知识巩固： -2
    """
    activity = models.IntegerField("活动id", default=0)

    class Meta:
        verbose_name = "5.4 活动点击记录"
        verbose_name_plural = verbose_name
