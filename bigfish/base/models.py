import jsonfield
from django.db import models

from django.utils import timezone

from bigfish.base.choices import GRADE_CHOICE, QUESTION_TYPE_CHOICE, TERM_CHOICE

media_path = None


class AbsBase(models.Model):
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True
        ordering = ['id']


class AbsTitleBase(AbsBase):
    title = models.CharField("名称", max_length=250, blank=True, default="")

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return '{}'.format(self.title)


class AbsExtraTitle(AbsBase):
    title = models.CharField("名称", max_length=250, default="")
    en_title = models.CharField("英语名", max_length=250, default="", blank=True)
    subtitle = models.CharField("子标题", max_length=250, blank=True, default='')
    short_name = models.CharField("缩略名", max_length=250, default="", blank=True)

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return '{}'.format(self.title)


class AbsMedia(models.Model):
    """
    多媒体
    """
    video = models.FileField("视频", upload_to=media_path, blank=True)
    audio = models.FileField("音频", upload_to=media_path, blank=True)
    image = models.ImageField("图片", upload_to=media_path, blank=True)

    class Meta:
        abstract = True


class AbsHis(models.Model):
    his_description = models.TextField("写入历史描述", blank=True, null=True)
    his_create_time = models.DateTimeField("写入历史时间", auto_now_add=True)

    class Meta:
        abstract = True


class AbsRpt(models.Model):
    start_time = models.DateTimeField("开始时间", default=timezone.now)
    finish_time = models.DateTimeField("结束时间", default=timezone.now)

    class Meta:
        abstract = True


class AbsDateRpt(models.Model):
    start_date = models.DateField("开始日期", default=timezone.now)
    finish_date = models.DateField("结束日期", default=timezone.now)

    class Meta:
        abstract = True


class AbsPersonalRpt(models.Model):
    # 个人信息
    province_code = models.IntegerField("省份编码", default=0, blank=True)
    province_name = models.CharField("省份名称", max_length=200, blank=True, default="")
    city_code = models.IntegerField("城市编码", default=0, blank=True)
    city_name = models.CharField("城市名称", max_length=200, blank=True, default="")
    area_id = models.IntegerField("地区码", default=0, blank=True)
    area_name = models.CharField("地区名称", max_length=200, blank=True, default="")
    school_id = models.IntegerField("学校ID", blank=True, default=0)
    school_name = models.CharField("学校名称", max_length=200, blank=True, default="")
    short_name = models.CharField("学校简称", max_length=200, blank=True, default="")
    grade_name = models.IntegerField("年级", choices=GRADE_CHOICE, default=1)
    klass_id = models.IntegerField("班级ID", blank=True, default=0)
    klass_name = models.CharField("班级程名称", max_length=200, blank=True, default="")
    username = models.CharField("账号", max_length=200, blank=True, default="")
    realname = models.CharField("真实姓名", max_length=200, blank=True, default="")
    nickname = models.CharField("昵称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True


class AbsPublishRpt(models.Model):
    # 教材信息
    publish_name = models.CharField("教材名称", max_length=200, blank=True, default="")
    textbook_id = models.IntegerField("教材", blank=True, default=0)
    textbook_name = models.CharField("教材名称", max_length=200, blank=True, default="")
    term_num = models.IntegerField("学期", choices=TERM_CHOICE, default=1)
    unit_name = models.CharField("单元名称", max_length=200, blank=True, default="")
    lesson_name = models.CharField("课程名称", max_length=200, blank=True, default="")
    lesson_order = models.PositiveIntegerField("课程序号", null=True, blank=True, default=0)

    class Meta:
        abstract = True


class AbsActRpt(models.Model):
    first_type = models.IntegerField("活动一级分类", default=0)
    second_type = models.IntegerField("活动二级分类", default=0)
    first_type_name = models.CharField("活动一级分类名称", max_length=200, default="")
    second_type_name = models.CharField("活动二级分类名称", max_length=200, default="")
    third_type = models.CharField("活动三级分类", max_length=200, default="")
    act_title = models.CharField("活动名称", max_length=200, blank=True, default="")
    act_subtitle = models.CharField("活动子标题", max_length=200, blank=True, default="")
    is_must = models.BooleanField("是否必学", default=False)
    is_recommend = models.BooleanField("是否推荐", default=False)

    class Meta:
        abstract = True


class AbsActDataRpt(models.Model):
    answer_right_times = models.PositiveIntegerField("答对次数", blank=True, default=0)
    answer_wrong_time = models.PositiveIntegerField("答错次数", blank=True, default=0)
    answer_max = models.PositiveIntegerField("回答题目总数", blank=True, default=0)  # 可不传
    question_total_num = models.PositiveIntegerField("题目总数", blank=True, default=0)  # 可不传
    all_time = models.PositiveIntegerField("总用时", blank=True, default=0)  # 可不传
    is_complete = models.BooleanField("是否完成", default=False)  # 可不传
    right_rate = models.FloatField("正确率", default=0.0)  # 可不传
    max_right_number = models.PositiveIntegerField("最大连对次数", blank=True, default=0)
    score = models.FloatField("成绩", blank=True, default=0)

    class Meta:
        abstract = True


class AbsQuestionRpt(models.Model):
    question_id = models.IntegerField("题目ID", default=0, blank=True)
    is_right = models.SmallIntegerField("正确错误")
    question_type = models.IntegerField("题目类型", choices=QUESTION_TYPE_CHOICE, default=1)
    difficulty = models.IntegerField("难度系数", default=10)
    voice_url = models.CharField("音频地址", max_length=500, default="", blank=True)
    answer = jsonfield.JSONField("答题", blank=True, null=True, default={})
    purpose = models.CharField("练习目的", max_length=200, blank=True, default='')

    class Meta:
        abstract = True


class AbsClick(models.Model):
    add_time = models.DateTimeField("添加时间", default=timezone.now)
    description = models.TextField("描述", blank=True, default="")

    class Meta:
        abstract = True
