import os

from django.conf import settings
from django.db import models

from bigfish.apps.collection.apps import MEDIA_PREFIX
from bigfish.apps.textbooks.models import Activity
from bigfish.apps.versus.models import Versus


def media_path(instance, filename):
    """
    成就图标存储路径
    """
    if isinstance(instance, UserVoice):
        path = os.path.join(MEDIA_PREFIX, 'voice', filename)
    elif isinstance(instance, UserPhoto):
        path = os.path.join(MEDIA_PREFIX, 'photo', filename)
    else:
        path = os.path.join(MEDIA_PREFIX, 'unknown', filename)

    return path


class UserVoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='%(app_label)s_%(class)s_user',
                             blank=True, null=True,
                             verbose_name='用户')
    activity = models.ForeignKey(Activity,
                                 related_name='%(app_label)s_%(class)s_activity',
                                 blank=True, null=True,
                                 verbose_name='活动')

    source = models.FileField("资源", upload_to=media_path, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "用户上传音频"
        verbose_name_plural = verbose_name


class UserPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='%(app_label)s_%(class)s_user',
                             verbose_name='用户')
    versus = models.ForeignKey(Versus,
                               related_name='%(app_label)s_%(class)s_versus',
                               blank=True, null=True,
                               verbose_name='对战')
    source = models.FileField("资源", upload_to=media_path, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "用户上传图片"
        verbose_name_plural = verbose_name
