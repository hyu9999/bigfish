from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from bigfish.apps.achievement.abs_models import AbsAchievement
from bigfish.apps.resources.models import Image
from bigfish.base.choices import FUNCTION_CHOICE, DESC_CHOICE, ACHIEVE_STATUS_CHOICE


class Achievement(AbsAchievement):
    """
    成就
    """
    function_type = models.IntegerField('功能类型', choices=FUNCTION_CHOICE, default=1)
    desc_type = models.IntegerField('描述类型', choices=DESC_CHOICE, default=1)
    reward = models.CharField('奖励描述', max_length=100, blank=True)
    all_need_num = models.IntegerField("获得成就所需个数", default=0, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        verbose_name = "成就"
        verbose_name_plural = verbose_name


class UserAchievement(AbsAchievement):
    """
    用户成就
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户",
                              on_delete=models.CASCADE, related_name='owner')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='achievement', default=1)
    status = models.IntegerField('状态', choices=ACHIEVE_STATUS_CHOICE, default=1)
    progress = models.FloatField('进度', max_length=100, default=0.0)
    current_num = models.IntegerField("获得成就已经完成个数", default=0)

    def __str__(self):
        return '{} {}'.format(self.owner.username, self.achievement.title)

    class Meta:
        verbose_name = "用户成就"
        verbose_name_plural = verbose_name

    @classmethod
    def get_status_by_progress(cls, progress):
        if not progress:
            return '1'
        try:
            f_progress = float(progress)
        except:
            return '1'
        if f_progress == 0.0:
            return '1'
        elif f_progress == 1.0:
            return '3'
        else:
            return '2'
