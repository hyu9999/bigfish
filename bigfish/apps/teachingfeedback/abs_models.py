from django.db import models


class AbsData(models.Model):
    right_rate = models.FloatField("平均正确率", blank=True, default=0.0)
    total_duration = models.FloatField("总时长", blank=True, default=0.0)

    class Meta:
        abstract = True


class AbsAppraisalData(models.Model):
    score = models.FloatField("总体评分", blank=True, default=0.0)
    word_score = models.FloatField("词汇成绩", blank=True, default=0.0)
    sentence_score = models.FloatField("句型成绩", blank=True, default=0.0)
    remark = models.TextField("评语", blank=True, default="")

    class Meta:
        abstract = True
