import os

import jsonfield
from django.db import models

from bigfish.apps.resources.models import Image, Video
from bigfish.apps.textbooks.abs_models import AbsTextbooks
from bigfish.base.choices import GRADE_CHOICE, TERM_CHOICE, FIRST_TYPE_CHOICE, SECOND_TYPE_CHOICE, ACT_DISPLAY_CHOICES
from bigfish.base.models import AbsClick

MEDIA_PREFIX = 'textbooks'


def media_directory(instance, filename):
    if isinstance(instance, PublishVersion):
        path = os.path.join(
            MEDIA_PREFIX,
            'publish-{}'.format(instance.pk),
            filename
        )
    elif isinstance(instance, Textbook):
        path = os.path.join(
            MEDIA_PREFIX,
            'publish-{}'.format(instance.publish_id),
            'textbook-{}'.format(instance.pk),
            filename
        )
    elif isinstance(instance, Unit):
        path = os.path.join(
            MEDIA_PREFIX,
            'publish-{}'.format(instance.textbook.publish_id),
            'textbook-{}'.format(instance.textbook_id),
            'unit-{}'.format(instance.pk),
            filename
        )
    elif isinstance(instance, Lesson):
        path = os.path.join(
            MEDIA_PREFIX,
            'publish-{}'.format(instance.unit.textbook.publish_id),
            'textbook-{}'.format(instance.unit.textbook_id),
            'unit-{}'.format(instance.unit.pk),
            'lesson-{}'.format(instance.pk),
            filename
        )
    elif isinstance(instance, Activity):
        path = os.path.join(
            MEDIA_PREFIX,
            'activity',
            '{}'.format(instance.pk),
            'media',
            filename
        )
    else:
        path = os.path.join(MEDIA_PREFIX, 'unknown', filename)

    return path


class PublishVersion(AbsTextbooks):
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    word_lib_num = models.PositiveIntegerField("默认题库题数", default=20)
    backup_lib_num = models.PositiveIntegerField("备用题库题数", default=10)

    class Meta:
        ordering = ('order',)
        verbose_name = "1. 教材版本"
        verbose_name_plural = verbose_name


class Textbook(AbsTextbooks):
    image = models.ForeignKey(Image, verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    publish = models.ForeignKey(PublishVersion, verbose_name="教材版本",
                                on_delete=models.CASCADE,
                                related_name="%(app_label)s_%(class)s_publish")
    grade = models.IntegerField("年级", choices=GRADE_CHOICE, default=11)
    term = models.IntegerField("学期", choices=TERM_CHOICE, default=1)

    class Meta:
        ordering = ('publish', 'order',)
        verbose_name = "2. 教材册目"
        verbose_name_plural = verbose_name


class Unit(AbsTextbooks):
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    textbook = models.ForeignKey(Textbook, verbose_name="教材册目",
                                 on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_textbook")
    video = models.ForeignKey(Video,
                              verbose_name="情景介绍",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_video")

    class Meta:
        ordering = ('textbook', 'order',)
        verbose_name = "3. 单元"
        verbose_name_plural = verbose_name


class Lesson(AbsTextbooks):
    unit = models.ForeignKey('Unit', verbose_name="单元", on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_unit")
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    video = models.ForeignKey(Video,
                              verbose_name="视频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_video")

    class Meta:
        ordering = ('unit', 'order',)
        verbose_name = "4. 课程"
        verbose_name_plural = verbose_name


class KnowledgeMap(AbsTextbooks):
    unit = models.OneToOneField(Unit,
                                on_delete=models.CASCADE,
                                related_name='knowledge_map',
                                primary_key=True)
    knowledge_data = models.TextField("知识地图数据", null=True, blank=True)

    class Meta:
        ordering = ('order',)
        verbose_name = "知识地图"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "Knowledge Map for {}".format(self.unit.title)


class PrepareAdvise(models.Model):
    purpose = jsonfield.JSONField("活动目的", blank=True, default={})
    step = jsonfield.JSONField("步骤", blank=True, default={})
    task = jsonfield.JSONField("教师任务", blank=True, default={})
    statement = jsonfield.JSONField("教师话述", blank=True, default={})
    video = models.ForeignKey(Video, verbose_name="视频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_video")

    class Meta:
        verbose_name = "5.3 备课建议"
        verbose_name_plural = verbose_name


class ActTab(AbsTextbooks):
    publish = models.ForeignKey(PublishVersion, verbose_name="教材版本",
                                on_delete=models.CASCADE, blank=True, null=True,
                                related_name="%(app_label)s_%(class)s_publish")
    pc_image = models.ForeignKey(Image,
                                 verbose_name="pc端图片",
                                 blank=True, null=True,
                                 related_name="%(app_label)s_%(class)s_pc_image")
    app_image = models.ForeignKey(Image,
                                  verbose_name="app端图片",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_app_image")
    is_must = models.BooleanField("是否必学", default=False)

    class Meta:
        ordering = ('order',)
        verbose_name = "5.1 活动页签"
        verbose_name_plural = verbose_name


class ActType(models.Model):
    first_type = models.IntegerField("一级分类", choices=FIRST_TYPE_CHOICE, default=1)
    second_type = models.IntegerField("二级分类", choices=SECOND_TYPE_CHOICE, default=1)
    third_type = models.CharField("三级分类", max_length=250)

    class Meta:
        verbose_name = "5.2 活动类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s-%s-%s' % (self.get_first_type_display(), self.get_second_type_display(), self.third_type)


class Activity(AbsTextbooks):
    publish = models.ForeignKey('PublishVersion',
                                verbose_name="教材版本",
                                on_delete=models.CASCADE,
                                related_name='%(app_label)s_%(class)s_publish')
    textbook = models.ForeignKey('Textbook',
                                 verbose_name="教材",
                                 on_delete=models.CASCADE,
                                 related_name='%(app_label)s_%(class)s_textbook')
    unit = models.ForeignKey('Unit',
                             verbose_name="单元",
                             on_delete=models.CASCADE,
                             related_name='%(app_label)s_%(class)s_unit')
    lesson = models.ForeignKey('Lesson',
                               verbose_name="课程",
                               on_delete=models.CASCADE,
                               related_name='%(app_label)s_%(class)s_lesson')
    act_tab = models.ForeignKey(ActTab,
                                verbose_name="活动页签",
                                related_name="%(app_label)s_%(class)s_act_tab",
                                blank=True, null=True)
    act_type = models.ForeignKey(ActType,
                                 verbose_name="活动类型", null=True, blank=True,
                                 related_name="%(app_label)s_%(class)s_act_type",
                                 default=1)
    is_recommend = models.BooleanField("是否推荐", default=False)
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    # 前端展示题型时使用
    display_type = models.IntegerField("题型展示分类", choices=ACT_DISPLAY_CHOICES, default=1)
    # 活动基础积分
    integral = models.FloatField("积分", default=0.0)
    suggested_time = models.FloatField("建议时间", default=0.0)
    """
    # 类型一:文章
    {
       "article_id":[123]
    }
    # 类型二:题目
    {
        "question_id":[1,2,3]
    }
    # 类型三:单词
    {
        "word_id":[1,2,3]
    }
    # 类型四:人际活动 process
    {
        "progress":[
        {"order":1, "title":"xxx", "image_id":1, "audio_id":1, "video_id":1, "text":"xxx", "answer":"xxxx"}
        {"order":2, "title":"xxx", "image_id":2, "audio_id":2, "video_id":2, "text":"xxx", "answer":"xxxx"}
        ]
    }
    # 类型五:资源 res
    {
        "res":[
        {"image_id":1,}
        {"audio_id":1,}
        {"video_id":1,}
        ]
    }
    """
    rule = jsonfield.JSONField("规则描述", blank=True, default={})
    rule_data = jsonfield.JSONField("规则数据", blank=True, default={})
    """
    ["xx", "xxx"]
    """
    knowledge_point = jsonfield.JSONField("知识点", blank=True, default={})
    en_des = models.TextField("英文描述", blank=True, default="")
    prepare_advise = models.ForeignKey(PrepareAdvise, verbose_name="备课建议",
                                       blank=True, null=True,
                                       related_name='%(app_label)s_%(class)s_prepare_advise')

    class Meta:
        verbose_name = "5. 活动"
        verbose_name_plural = verbose_name
