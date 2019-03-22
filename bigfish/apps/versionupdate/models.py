from django.db import models
from bigfish.apps.areas.models import Area
from bigfish.apps.schools.models import School, Klass
from bigfish.apps.textbooks.models import PublishVersion
from bigfish.base.choices import OPERATE_CHOICE, IDENTITY_CHOICE
from bigfish.base.const import STUDENT


class Abstract(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now=True)
    note = models.TextField('备注', blank=True, null=True)

    class Meta:
        abstract = True


class AbsChange(models.Model):
    folder_name = models.CharField('文件夹路径', max_length=250, default='')
    last_size = models.BigIntegerField('变更前大小', default=0)
    surrent_size = models.BigIntegerField('变更后大小', default=0)
    change_size = models.BigIntegerField('改变大小', default=0)
    operate = models.IntegerField('操作', choices=OPERATE_CHOICE, default=1)

    class Meta:
        abstract = True


class Version(Abstract):
    """
    正式服：F
    测试服：T
    PEP包：P
    精通包：J

    eg:(F|T)&(P|J) 1.0.0

    """
    version_name = models.CharField('版本名', max_length=250)
    version_code = models.PositiveIntegerField('版本号', blank=True, default=0, unique=True)
    apk_code = models.PositiveIntegerField('包版本号', blank=True, default=0)
    folder_name = models.CharField('主目录名称', max_length=250, blank=True, null=True)
    username = models.CharField('负责人名称', max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = '版本信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}'.format(self.version_name)


class IdentityVersion(Abstract):
    identity = models.IntegerField("角色", choices=IDENTITY_CHOICE, default=STUDENT)
    version = models.ForeignKey(Version,
                                related_name='%(app_label)s_%(class)s_identity_version',
                                on_delete=models.CASCADE,
                                verbose_name='版本号')
    apk_name = models.CharField('包名称', max_length=250, default=0)
    apk_size = models.IntegerField('apk文件大小', default=0)
    folder_name = models.CharField('主目录名称', max_length=250, default='')  # example: media/version_name
    username = models.CharField('负责人名称', max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = '角色对应版本'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}{}'.format(self.get_identity_display(), self.version)


class UpdatePublish(Abstract, AbsChange):
    identity = models.ForeignKey(IdentityVersion,
                                 related_name='%(app_label)s_%(class)s_update_publish',
                                 on_delete=models.CASCADE,
                                 verbose_name='角色版本号')
    publish = models.ForeignKey(PublishVersion,
                                related_name='%(app_label)s_%(class)s_publish',
                                on_delete=models.CASCADE,
                                verbose_name='教材版本')

    class Meta:
        verbose_name = '更新教材信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{} {}'.format(self.publish, self.identity.version.version_name)


class UpdateConfig(Abstract):
    LEVEL_CHOICES = (
        (1, '全局'),
        (2, '区域'),
        (3, '学校'),
    )
    update_publish = models.ForeignKey(UpdatePublish,
                                       on_delete=models.CASCADE,
                                       related_name='%(app_label)s_%(class)s_update_publish',
                                       verbose_name='教材版本号')
    school = models.ForeignKey(School,
                               on_delete=models.SET_NULL,
                               related_name='%(app_label)s_%(class)s_update_school',
                               verbose_name='学校',
                               blank=True,
                               null=True)
    area = models.ForeignKey(Area,
                             on_delete=models.SET_NULL,
                             related_name='%(app_label)s_%(class)s_update_area',
                             verbose_name='区域',
                             blank=True,
                             null=True)
    klass = models.ForeignKey(Klass,
                              on_delete=models.SET_NULL,
                              related_name='%(app_label)s_%(class)s_update_klass',
                              verbose_name='班级',
                              blank=True,
                              null=True)
    level = models.IntegerField('级别', choices=LEVEL_CHOICES, default=1)
    complete_num = models.IntegerField('实际更新数量', default=0)
    update_time = models.DateTimeField('更新时间', auto_now_add=True)

    class Meta:
        verbose_name = '更新区域配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.update_publish.publish.title


class UpdateDetail(Abstract, AbsChange):
    update_publish = models.ForeignKey(UpdatePublish,
                                       on_delete=models.CASCADE,
                                       related_name='%(app_label)s_%(class)s_update_publish',
                                       verbose_name='教材版本号', )
    zip_name = models.CharField('压缩文件', max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = '更新资源目录详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.update_publish.publish.title


class UpdateException(Abstract):
    version = models.ForeignKey(Version,
                                on_delete=models.CASCADE,
                                related_name='version',
                                verbose_name='版本号'
                                )
    update_publish = models.ForeignKey(UpdatePublish,
                                       on_delete=models.CASCADE,
                                       related_name='%(app_label)s_%(class)s_update_publish',
                                       verbose_name='教材版本号'
                                       )
    identity = models.ForeignKey(IdentityVersion,
                                 on_delete=models.CASCADE,
                                 related_name='%(app_label)s_%(class)s_identity',
                                 verbose_name='角色版本号')
    username = models.CharField('账号', max_length=250)
    message = models.CharField('错误信息', max_length=250)
    publish = models.CharField('教材', max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = '更新异常记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}:{}'.format(self.username, self.message)


class SourceDetail(Abstract):
    folder = models.CharField('文件夹路径', max_length=250)
    username = models.CharField('账号', max_length=250)
    update_time = models.DateTimeField('更新时间', auto_now_add=True)

    class Meta:
        verbose_name = '全资源目录详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
