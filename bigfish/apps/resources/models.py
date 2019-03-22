import logging
import os

import jsonfield
from django.db import models

from bigfish.apps.resources.abs_models import AbsSource
from bigfish.apps.resources.apps import MEDIA_PREFIX
from bigfish.base.models import AbsTitleBase

logger = logging.getLogger('django')


def media_path(instance, filename):
    if isinstance(instance, Video):
        path = os.path.join(MEDIA_PREFIX, 'prores', 'video', filename)
    elif isinstance(instance, Audio):
        path = os.path.join(MEDIA_PREFIX, 'prores', 'audio', 'sysaudio', filename)
    elif isinstance(instance, Amazon):
        path = os.path.join(MEDIA_PREFIX, 'prores', 'audio', 'amazonaudio', filename)
    elif isinstance(instance, Animation):
        path = os.path.join(MEDIA_PREFIX, 'prores', 'animation', filename)
    elif isinstance(instance, SpecialEffect):
        path = os.path.join(MEDIA_PREFIX, 'prores', 'special_effect', filename)
    elif isinstance(instance, Image):
        path = os.path.join(MEDIA_PREFIX, 'prores', 'image', 'ui', filename)
    else:
        path = os.path.join(MEDIA_PREFIX, 'prores', 'unknown', filename)
    return path


class ImageType(models.Model):
    title = models.CharField("名称", max_length=100)
    order = models.IntegerField("排序", blank=True, default=0)
    description = models.TextField("描述", blank=True, default="")

    class Meta:
        verbose_name = '图片类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)


class Image(AbsTitleBase):
    image_type = models.ForeignKey(ImageType, verbose_name="图片类型",
                                   blank=True, null=True,
                                   related_name="%(app_label)s_%(class)s_image_type")
    res = models.FileField(upload_to=media_path, verbose_name='资源', blank=True, null=True)

    class Meta:
        ordering = ('id',)
        verbose_name = '图片'
        verbose_name_plural = verbose_name


class AudioType(models.Model):
    title = models.CharField("名称", max_length=100)
    order = models.IntegerField("排序", blank=True, default=0)
    description = models.TextField("描述", blank=True, default="")

    class Meta:
        verbose_name = '音频类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)


class Audio(AbsTitleBase):
    audio_type = models.ForeignKey(AudioType, verbose_name="音频类型",
                                   blank=True, null=True,
                                   related_name="%(app_label)s_%(class)s_audio_type")
    res = models.FileField(upload_to=media_path, verbose_name='资源', blank=True, null=True)
    image = models.ForeignKey(Image, verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")

    class Meta:
        verbose_name = '音频'
        verbose_name_plural = verbose_name


class VideoType(models.Model):
    title = models.CharField("名称", max_length=100)
    order = models.IntegerField("排序", blank=True, default=0)
    description = models.TextField("描述", blank=True, default="")

    class Meta:
        verbose_name = '视频类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)


class Video(AbsTitleBase):
    video_type = models.ForeignKey(VideoType, verbose_name="视频类型",
                                   blank=True, null=True,
                                   related_name="%(app_label)s_%(class)s_video_type")
    res = models.FileField(upload_to=media_path, verbose_name='资源', blank=True, null=True)
    image = models.ForeignKey(Image, verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name


class ActImage(models.Model):
    activity_name = models.CharField("活动名称", max_length=100)
    image = models.ForeignKey(Image, verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")

    class Meta:
        verbose_name = '活动封面'
        verbose_name_plural = verbose_name


class Animation(AbsTitleBase):
    res = models.FileField(upload_to=media_path, verbose_name='资源', blank=True, null=True)
    param = jsonfield.JSONField("参数", blank=True, default={})

    class Meta:
        verbose_name = '动画'
        verbose_name_plural = verbose_name


class SpecialEffect(AbsTitleBase):
    res = models.FileField(upload_to=media_path, verbose_name='资源', blank=True, null=True)
    param = jsonfield.JSONField("参数", blank=True, default={})

    class Meta:
        verbose_name = '特效'
        verbose_name_plural = verbose_name


class Pet(AbsTitleBase):
    image = models.ForeignKey(Image, verbose_name="图片",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_image")
    shield = models.IntegerField("护盾值", blank=True, default=0)
    attack = models.IntegerField("攻击值", blank=True, default=0)
    crit = models.FloatField("暴击值", blank=True, default=0)
    price = models.IntegerField("价格", default=0)
    is_free = models.BooleanField("是否赠送英雄", default=False)
    thumbnail = models.ForeignKey(Image, verbose_name="缩略图",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_thumbnail")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "宠物"
        verbose_name_plural = verbose_name


class Amazon(AbsTitleBase):
    """
    亚马逊TTs
    """
    text = models.TextField("文本内容", default="")
    tts_boy = models.FileField('男声', upload_to=media_path, blank=True)
    tts_girl = models.FileField('女声', upload_to=media_path, blank=True)

    class Meta:
        verbose_name = '亚马逊语音资源'
        verbose_name_plural = verbose_name


class LocResInfo(AbsTitleBase):
    loc_url = models.CharField("服务器地址", max_length=200, blank=True, default="")

    class Meta:
        verbose_name = '本地资源服务器'
        verbose_name_plural = verbose_name
