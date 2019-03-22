import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.apps.classrooms.models import Classroom
from bigfish.apps.questions.models import Question
from bigfish.apps.textbooks.models import Activity
from bigfish.base.choices import MASTER_LEVEL, DATA_SOURCE
from bigfish.base.models import AbsPublishRpt, AbsPersonalRpt, AbsActRpt


class WrongTopic(AbsPublishRpt, AbsPersonalRpt, AbsActRpt):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    classroom = models.ForeignKey(Classroom, verbose_name="课堂",
                                  on_delete=models.CASCADE,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  blank=True, null=True, help_text="课堂")
    activity = models.ForeignKey(Activity, verbose_name="活动",
                                 on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True, help_text="活动")
    question = models.ForeignKey(Question, verbose_name="题目",
                                 related_name="%(app_label)s_%(class)s_question",
                                 blank=True, null=True,
                                 help_text="题目")
    kp_name = models.CharField("知识点名称", max_length=200, blank=True, default="")
    kp_coding = models.UUIDField("知识点编码", blank=True, default=uuid.uuid4)
    master_level = models.IntegerField("掌握程度", choices=MASTER_LEVEL, default=1)

    """
    1.任务下展示格式：任务名称（布置的任务XX）- 单元 - lesson - 活动名
    2.自主学习展示格式：自主学习 - 单元 - lesson - 活动名
    3.作业下展示格式：2018-08-11 周三 布置的作业
    4.错题本下展示格式：自主学习-错题本-综合复习

    """
    data_source = models.IntegerField("数据来源", choices=DATA_SOURCE, default=1)
    ever_wrong = models.BooleanField("是否做错过", default=False)
    scene = models.CharField("错误场景", max_length=200, blank=True, default="")
    update_time = models.DateTimeField("更新时间", auto_now=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "错题本"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.username, self.kp_name)


class WrongTopicHis(AbsPublishRpt, AbsPersonalRpt, AbsActRpt):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    classroom = models.ForeignKey(Classroom, verbose_name="课堂",
                                  on_delete=models.CASCADE,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  blank=True, null=True, help_text="课堂")
    activity = models.ForeignKey(Activity, verbose_name="活动",
                                 on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity",
                                 blank=True, null=True, help_text="活动")
    question = models.ForeignKey(Question, verbose_name="题目",
                                 related_name="%(app_label)s_%(class)s_question",
                                 blank=True, null=True,
                                 help_text="题目")
    wrong_topic = models.ForeignKey(WrongTopic,
                                    on_delete=models.CASCADE,
                                    verbose_name="错题本",
                                    related_name="%(app_label)s_%(class)s_wrong_topic")
    # 知识点
    kp_name = models.CharField("知识点名称", max_length=200, blank=True, default="")
    kp_coding = models.UUIDField("知识点编码", blank=True, default=uuid.uuid4)
    master_level = models.IntegerField("掌握程度", choices=MASTER_LEVEL, default=1)
    """
    1.任务下展示格式：任务名称（布置的任务XX）- 单元 - lesson - 活动名
    2.自主学习展示格式：自主学习 - 单元 - lesson - 活动名
    3.作业下展示格式：2018-08-11 周三 布置的作业
    4.错题本下展示格式：自主学习-错题本-综合复习

    """
    data_source = models.IntegerField("数据来源", choices=DATA_SOURCE, default=1)
    is_pop = models.BooleanField("是否弹出", default=False)  # 进入错题本时，在非综合复习中达到lv6时，标记为True,其他情况为False
    scene = models.CharField("错误场景", max_length=200, blank=True, default="")
    update_time = models.DateTimeField("更新时间", default=timezone.now)
    add_time = models.DateTimeField("添加时间", default=timezone.now)

    class Meta:
        verbose_name = "错题本历史记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.username, self.kp_name)
