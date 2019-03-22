from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from bigfish.apps.classrooms.models import Classroom
from bigfish.apps.contents.models import TextbookWord
from bigfish.apps.schools.models import Klass
from bigfish.base.choices import RESULT_CHOICE, VERSUS_QUESTION_TYPE_CHOICE, USER_TYPE_CHOICE


class AbstractVersus(models.Model):
    competitor = models.ForeignKey('self', blank=True, null=True, related_name='competitor_user')

    class Meta:
        abstract = True


class Versus(AbstractVersus):
    COMPETITOR_CHOICE = (
        (0, 'AI'),
        (1, '用户'),
    )
    COMPLETE_TYPE_CHOICE = (
        (0, '未完成'),
        (1, '正常退出'),
        (2, '完成'),
    )
    PK_TYPE_CHOICE = (
        (0, '任务对战'),
        (1, '自由对战'),
    )
    RESULT_CHOICE = (
        (0, '负'),
        (1, '胜'),
    )
    classroom = models.ForeignKey(Classroom,
                                  verbose_name="课堂",
                                  on_delete=models.CASCADE,
                                  related_name="%(app_label)s_%(class)s_classroom",
                                  help_text="课堂")
    competitor_type = models.IntegerField("对手类型", choices=COMPETITOR_CHOICE, default=0)
    complete_type = models.IntegerField("完成状态", choices=COMPLETE_TYPE_CHOICE, default=0)
    pk_type = models.IntegerField("对战方式", choices=PK_TYPE_CHOICE, default=0)
    start_time = models.DateTimeField(verbose_name='对战开始时间')
    end_time = models.DateTimeField(verbose_name='对战结束时间')
    # user
    pk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pk_user',
                                verbose_name='对战者')
    head_icon = models.CharField('头像框', max_length=200, blank=True, null=True)
    pet_name = models.CharField('宠物名称', max_length=200, blank=True, null=True)
    speed = models.FloatField('答题速度（秒）', default=0)  # second
    score = models.IntegerField("总积分", default=0)
    real_score = models.IntegerField("实际得分", default=0)
    big_fishery = models.IntegerField("大渔币", default=0)
    pk_result = models.IntegerField("对战结果", choices=RESULT_CHOICE, default=0)
    right_times = models.IntegerField("答对题数", default=0)
    wrong_times = models.IntegerField("答错题数", default=0)
    total_times = models.IntegerField("答题总数", default=0)
    max_right_number = models.PositiveIntegerField("最大连对次数", default=0)
    # AI
    user_ai = models.CharField('对手昵称', max_length=200, blank=True, null=True, default="")
    ai_icon = models.CharField('对手头像', max_length=200, blank=True, null=True, default="")
    ai_icon_frame = models.CharField('对手头像框', max_length=200, blank=True, null=True, default="")
    pet_name_ai = models.CharField('对手宠物名称', max_length=200, blank=True, null=True, default="")
    speed_ai = models.FloatField('对手答题速度', blank=True, null=True, default=0)  # second
    score_ai = models.IntegerField("对手总积分", blank=True, null=True, default=0)
    real_score_ai = models.IntegerField("对手实际得分", blank=True, null=True, default=0)
    big_fishery_ai = models.IntegerField("对手大渔币", blank=True, null=True, default=0)
    pk_result_ai = models.IntegerField("对手对战结果", choices=RESULT_CHOICE, default=0)
    right_times_ai = models.IntegerField("对手答对题数", blank=True, null=True, default=0)
    wrong_times_ai = models.IntegerField("对手答错题数", blank=True, null=True, default=0)
    total_times_ai = models.IntegerField("对手答题总数", blank=True, null=True, default=0)
    max_right_number_ai = models.PositiveIntegerField("对手最大连对次数", blank=True, null=True, default=0)

    class Meta:
        ordering = ('id',)

    # def __str__(self):
    #     try:
    #         test_try = '{}({})'.format(self.pk_user.username, self.start_time)
    #     except Exception as e:
    #         print(e,self.id,self.pk_user.username, self.start_time)
    #         return  ""
    #     return ""


class VersusDetail(models.Model):
    versus = models.ForeignKey(Versus, on_delete=models.CASCADE, related_name='versus_details', verbose_name='对战ID')
    order = models.PositiveIntegerField('序号', default=1)
    user_type = models.IntegerField("用户类型", choices=USER_TYPE_CHOICE, default=0)
    word = models.ForeignKey(TextbookWord, related_name='word', verbose_name='单词')
    question_type = models.CharField("题型", max_length=200, choices=VERSUS_QUESTION_TYPE_CHOICE,
                                     default=1)
    result = models.IntegerField("结果", choices=RESULT_CHOICE, default=0)

    def __str__(self):
        return '{} {} {}'.format(self.get_user_type_display(), self.word, self.get_result_display())


class VersusReport(models.Model):
    title = models.CharField("名称", max_length=250, blank=True, default="")
    classroom = models.OneToOneField(Classroom,
                                     verbose_name="课堂",
                                     on_delete=models.CASCADE,
                                     related_name="%(app_label)s_%(class)s_classroom",
                                     help_text="课堂",
                                     primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    klass = models.ForeignKey(Klass,
                              verbose_name="班级", on_delete=models.CASCADE,
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_klass")

    summary = models.TextField("总结评价", blank=True, null=True)
    advise = models.TextField("指导建议", blank=True, null=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "战报"
        verbose_name_plural = verbose_name
