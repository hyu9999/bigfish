import logging

import jsonfield
from django.db import models
from django.utils import timezone

from bigfish.apps.contents.abs_models import AbsContents
from bigfish.apps.knowledgepoint.models import KnowledgePoint
from bigfish.apps.resources.models import Video, Audio, Image, Animation
from bigfish.apps.textbooks.models import Lesson
from bigfish.base.choices import ARTICLE_CLASSIFY
from bigfish.base.models import AbsTitleBase

logger = logging.getLogger('django')


class Article(AbsContents):
    classify = models.IntegerField("分类", choices=ARTICLE_CLASSIFY, default=1)
    video = models.ForeignKey(Video,
                              verbose_name="视频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_video")
    audio = models.ForeignKey(Audio,
                              verbose_name="音频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_audio")
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name


class Sentence(AbsContents):
    video = models.ForeignKey(Video,
                              verbose_name="视频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_video")
    audio = models.ForeignKey(Audio,
                              verbose_name="音频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_audio")
    image = models.ForeignKey(Image,
                              verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    knowledge_point = models.ForeignKey(KnowledgePoint,
                                        verbose_name="知识点",
                                        blank=True, null=True,
                                        related_name="%(app_label)s_%(class)s_knowledge_point")
    word_kp = models.ManyToManyField(KnowledgePoint, verbose_name="词汇知识点",
                                     blank=True, related_name="%(app_label)s_%(class)s_word_kp")
    integral = models.IntegerField("积分", blank=True, default=0)
    article = models.ForeignKey(Article,
                                verbose_name="文章",
                                related_name="sentence",
                                blank=True, null=True)
    # 相对时间戳
    start_timestamp = models.BigIntegerField("开始时间戳", blank=True, default=0)
    end_timestamp = models.BigIntegerField("结束时间戳", blank=True, default=0)
    duration = models.PositiveIntegerField("时间间隔", blank=True, default=0)
    start_time = models.DateTimeField("开始时间", default=timezone.now)
    end_time = models.DateTimeField("结束时间", default=timezone.now)
    role = models.ForeignKey(Image,
                             verbose_name="角色",
                             related_name="%(app_label)s_%(class)s_role",
                             blank=True, null=True)

    class Meta:
        ordering = ('id', 'order')
        verbose_name = '句子'
        verbose_name_plural = verbose_name


class WordType(AbsTitleBase):

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '词库单词分类'
        verbose_name_plural = verbose_name


class TextbookWord(AbsContents):
    word_type = models.ForeignKey('WordType', related_name='word_type', verbose_name="单词分类", blank=True, null=True)
    compatible_id = models.TextField('共容ID', blank=True, default="")
    knowledge_point = models.ForeignKey(KnowledgePoint, verbose_name="知识点",
                                        blank=True, null=True,
                                        related_name="%(app_label)s_%(class)s_knowledge_point")
    video = models.ForeignKey(Video, verbose_name="视频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_video")
    audio = models.ForeignKey(Audio, verbose_name="音频",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_audio")
    image = models.ManyToManyField(Image, verbose_name="图片", blank=True,
                                   related_name="%(app_label)s_%(class)s_image")
    animation = models.ManyToManyField(Animation, verbose_name="动画", blank=True,
                                       related_name="%(app_label)s_%(class)s_animation")
    sentence = models.TextField("例句", blank=True, default='')
    sentence_highlight = models.TextField("高亮例句", blank=True, default='')
    sentence_explain = models.TextField('例句释义', blank=True, default='')
    microtext = models.ForeignKey(Article, verbose_name="微语篇",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_microtext")
    integral = models.IntegerField("积分", blank=True, default=0)
    lesson = models.ForeignKey(Lesson, verbose_name="课程",
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_lesson")

    class Meta:
        verbose_name = '教材词汇'
        verbose_name_plural = verbose_name
