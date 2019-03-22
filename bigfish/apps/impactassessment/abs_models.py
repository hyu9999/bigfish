from django.db import models

from bigfish.apps.schools.models import Term


class AbsFilterData(models.Model):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    publish_id = models.IntegerField("教材ID", default=0, db_index=True)
    publish_name = models.CharField("教材名称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True


class AbsComputeData(models.Model):
    right_rate = models.FloatField("正确率", blank=True, default=0.0)
    max_score = models.FloatField("最大成绩", blank=True, default=0.0)
    min_score = models.FloatField("最小成绩", blank=True, default=0.0)
    avg_score = models.FloatField("平均值", blank=True, default=0.0)
    use_duration = models.FloatField("使用时长", blank=True, default=0.0)
    interactive_num = models.IntegerField("平均交互次数", default=0)
    task_num = models.IntegerField("任务数", default=0)  # 使用次数

    class Meta:
        abstract = True
