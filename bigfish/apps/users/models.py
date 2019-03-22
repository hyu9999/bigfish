import logging
import os

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.base_session import AbstractBaseSession
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.db import models
from django.utils import six, timezone
from django.utils.translation import ugettext_lazy as _

from bigfish.apps.areas.models import Area
from bigfish.apps.resources.models import Pet
from bigfish.apps.schools.models import Klass, School
from bigfish.apps.textbooks.models import Lesson, Textbook, Unit
from bigfish.base.choices import IDENTITY_CHOICE, SEX_CHOICE, GRADE_CHOICE, ONLINE_STATUS_CHOICE, ACCOUNT_SOURCE_CHOICE
from bigfish.base.const import STUDENT, MALE
from bigfish.base.models import AbsTitleBase, AbsRpt, AbsBase

logger = logging.getLogger('django')


def media_path(instance, filename):
    if isinstance(instance, BigfishUser):
        path = os.path.join('res', 'ProRes', 'image', 'headicon', filename)
    else:
        path = os.path.join('res', 'ProRes', 'image', 'unknown', filename)
    return path


class BigfishUser(AbstractBaseUser, PermissionsMixin):
    hf_id = models.CharField("hf_id", max_length=200, blank=True, default="")
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def clean(self):
        super(BigfishUser, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    identity = models.IntegerField("角色", choices=IDENTITY_CHOICE, default=STUDENT)
    sex = models.IntegerField("性别", choices=SEX_CHOICE, default=MALE)
    realname = models.CharField("真实姓名", max_length=40, blank=True)
    """
    修改方式： 
    1.删除表users_userklassrelationship
    2.更改表名users_userprofile_attend_class 为users_userklassrelationship
    3.更改migrations里的py文件

    4.执行
    """
    account_source = models.IntegerField("账号来源", choices=ACCOUNT_SOURCE_CHOICE, default=1)
    school = models.ForeignKey(School,
                               verbose_name="学校",
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_school")
    attend_class = models.ManyToManyField(Klass, verbose_name="学校", blank=True,
                                          related_name="person", through='UserKlassRelationship')
    address = models.CharField("地址", max_length=500, blank=True)
    nickname = models.CharField("昵称", max_length=40, blank=True)
    telephone = models.CharField("手机号", max_length=20, blank=True)

    modified = models.DateTimeField("修改时间", auto_now=True)
    icon = models.FileField(upload_to=media_path, verbose_name='资源', blank=True, null=True)
    first_login = models.BooleanField('是否首次登录', default=True)
    attention_num = models.IntegerField("用户关注数", blank=True, default=0)
    fans_num = models.IntegerField("粉丝数", blank=True, default=0)
    area = models.ForeignKey(Area,
                             verbose_name="地区",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_area")
    control_area = models.ManyToManyField(Area,
                                          verbose_name="控制地区", blank=True,
                                          related_name="control_area")
    card_id = models.CharField('身份证号', max_length=200, blank=True)
    student_code = models.CharField('国家学籍号', max_length=200, blank=True)
    province_code = models.CharField('省学籍号', max_length=200, blank=True)
    is_formal = models.BooleanField("是否正式用户", default=True)

    class Meta:
        verbose_name = "1.1 用户"
        verbose_name_plural = verbose_name


class UserPosition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='position',
                             verbose_name='用户')
    position = models.CharField("位置", max_length=100, blank=True, default="[0,0]")
    note = models.CharField("备注信息", max_length=500, blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True, help_text="添加时间")

    class Meta:
        verbose_name = "用户位置信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}{}".format(self.user.username, self.position)


class UserCourse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='course',
                                verbose_name='用户',
                                primary_key=True)
    textbook = models.ForeignKey(Textbook, verbose_name="实时教材册目",
                                 related_name="%(app_label)s_%(class)s_textbook",
                                 blank=True, null=True)
    unit = models.ForeignKey(Unit,
                             verbose_name="实时单元",
                             related_name="%(app_label)s_%(class)s_unit",
                             blank=True, null=True)
    lesson = models.ForeignKey(Lesson, verbose_name="实时课程",
                               related_name="%(app_label)s_%(class)s_lesson",
                               blank=True, null=True)


class UserReg(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='reg',
                                verbose_name='用户',
                                primary_key=True)
    registration_id = models.CharField("设备注册ID", max_length=200, blank=True, default="")

    class Meta:
        verbose_name = "1.2 用户注册ID"
        verbose_name_plural = verbose_name


class UserOnline(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='online',
                                verbose_name='用户',
                                primary_key=True)
    last_login = models.DateTimeField('最近上线时间', blank=True, null=True)
    last_logout = models.DateTimeField('最近下线时间', blank=True, null=True)
    online_time = models.BigIntegerField('累计在线时长', default=0)
    is_online = models.BooleanField('是否在线', default=False)
    is_mark = models.BooleanField("是否被标记", default=False)
    status = models.IntegerField("状态", choices=ONLINE_STATUS_CHOICE, blank=True, default=0)

    class Meta:
        verbose_name = "1.3 用户在线情况"
        verbose_name_plural = verbose_name


class OnlineReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='%(app_label)s_%(class)s_user',
                             verbose_name='用户')
    login_time = models.DateTimeField('上线时间', default=timezone.now)
    logout_time = models.DateTimeField('下线时间', default=timezone.now)
    online_time = models.BigIntegerField('在线时长', blank=True, default=0)

    class Meta:
        verbose_name = "1.3.1 在线情况记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class UserKlassRelationship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="用户信息",
                             on_delete=models.CASCADE,
                             related_name="%(app_label)s_%(class)s_user",
                             help_text="用户信息"
                             )
    school = models.ForeignKey(School,
                               verbose_name="学校",
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_school")
    subject = models.CharField("科目", max_length=200, blank=True, default="")
    klass = models.ForeignKey(Klass,
                              verbose_name="班级",
                              on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_klass",
                              help_text="班级"
                              )
    study_progress = models.FloatField("学习进度", default=0.0, help_text="学习进度")
    update_time = models.DateTimeField("修改时间", auto_now=True, help_text="修改时间")
    add_time = models.DateTimeField("添加时间", auto_now_add=True, help_text="添加时间")
    # update_time = models.DateTimeField("修改时间", default=timezone.now, help_text="修改时间")
    # add_time = models.DateTimeField("添加时间",  default=timezone.now, help_text="添加时间")
    is_effect = models.BooleanField("是否有效", default=True, help_text="是否有效")
    is_default = models.BooleanField("是否默认", default=False, help_text="是否默认")
    remark = models.TextField("备注", default="", blank=True, help_text="备注")

    def save(self, *args, **kwargs):
        try:
            bf_obj = UserKlassRelationship.objects.get(id=self.id)
        except Exception as e:
            bf_obj = None
            logger.debug("[{}]未获取到原有信息！".format(e))
        super(UserKlassRelationship, self).save(*args, **kwargs)
        if bf_obj:
            if bf_obj.klass != self.klass:
                if bf_obj.klass.school != self.klass.school:
                    change_type = 2
                else:
                    change_type = 3
                UserChangeReport.objects.create(**{"user": self.user,
                                                   "old_klass_id": bf_obj.klass.id,
                                                   "old_klass_name": bf_obj.klass.title,
                                                   "old_school_id": bf_obj.klass.school.id,
                                                   "old_school_name": bf_obj.klass.school.title,
                                                   "old_grade": bf_obj.klass.grade,

                                                   "klass_id": self.klass.id,
                                                   "klass_name": self.klass.publish,
                                                   "school_id": self.klass.school.id,
                                                   "school_name": self.klass.school.title,
                                                   "grade": self.klass.grade,
                                                   "change_type": change_type,
                                                   "desc": "后台更新"})

    class Meta:
        verbose_name = "1.4 用户班级关系表"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'klass')

    def __str__(self):
        return "[{}]{}".format(self.user.username, self.klass.__str__())


class UserChangeReport(models.Model):
    CHANGE_CHOICE = (
        (1, "年级变更"),
        (2, "学校变更"),
        (3, "班级变更"),

    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="学生",
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True,
                             help_text="学生")
    change_type = models.IntegerField("变更类型", choices=CHANGE_CHOICE, default=1)
    # old
    old_school_id = models.IntegerField("原学校ID", blank=True, default=0)
    old_school_name = models.CharField("原学校名称", max_length=200, blank=True, default="")
    old_klass_id = models.IntegerField("原班级ID", blank=True, default=0)
    old_klass_name = models.CharField("原班级名称", max_length=200, blank=True, default="")
    old_grade = models.CharField("原年级", max_length=200, blank=True, default="")
    # new
    school_id = models.IntegerField("学校", blank=True, default=0)
    school_name = models.CharField("学校名称", max_length=200, blank=True, default="")
    klass_id = models.IntegerField("班级", blank=True, default=0, help_text="班级")
    klass_name = models.CharField("班级名称", max_length=200, blank=True, default="")
    grade = models.CharField("新年级", max_length=200, blank=True, default="")
    # operate
    operator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 verbose_name="修改人",
                                 related_name="%(app_label)s_%(class)s_operator",
                                 blank=True, null=True,
                                 help_text="修改人")
    desc = models.TextField("描述", default="", help_text="描述")
    add_time = models.DateTimeField("变更时间",
                                    auto_now_add=True,
                                    help_text="变更时间")

    class Meta:
        verbose_name = "1.5 用户信息变更记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} 信息变更".format(self.user.username)


class UserFeedback(models.Model):
    title = models.CharField("标题", max_length=100, default="", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    school = models.ForeignKey(School, on_delete=models.CASCADE,
                               verbose_name="学校",
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_school")
    grade = models.IntegerField("年级", choices=GRADE_CHOICE, default=11)
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE,
                              verbose_name="班级",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_klass")
    content = models.TextField("反馈信息", blank=True, default="")
    create_time = models.DateField("创建时间", auto_now_add=True)

    def __str__(self):
        return "{}-{}".format(self.user.username, self.title)

    class Meta:
        verbose_name = '1.6 用户反馈信息'
        verbose_name_plural = verbose_name


class UserUsedInfo(AbsTitleBase, AbsRpt):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    school = models.ForeignKey(School, on_delete=models.CASCADE,
                               verbose_name="学校",
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_school")
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE,
                              verbose_name="班级",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_klass")

    total_time = models.FloatField("总用时", default=0.0)

    class Meta:
        verbose_name = '1.7 用户使用app情况'
        verbose_name_plural = verbose_name


class UserWordHero(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    pet = models.ForeignKey(Pet,
                            on_delete=models.CASCADE,
                            verbose_name="宠物",
                            blank=True, null=True,
                            related_name="%(app_label)s_%(class)s_pet")
    is_active = models.BooleanField("是否上阵", default=False)

    class Meta:
        verbose_name = '1.8 用户宠物'
        verbose_name_plural = verbose_name


class UserScenariosReport(AbsBase):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                verbose_name="用户",
                                blank=True, null=True,
                                related_name="%(app_label)s_%(class)s_user")
    unit = models.ForeignKey(Unit,
                             on_delete=models.CASCADE,
                             verbose_name="单元",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_unit")

    class Meta:
        unique_together = ('teacher', 'unit')
        verbose_name = '1.9 用户情景介绍记录'
        verbose_name_plural = verbose_name


class BigFishSession(models.Model):
    account_id = models.IntegerField("账号", null=True, db_index=True)
    registration_id = models.CharField("设备注册ID", max_length=200, null=True)
    login_time = models.CharField("登陆时间", max_length=200, null=True)
    is_active = models.BooleanField("是否有效", default=True)

    class Meta:
        verbose_name = '1.10 session 扩展表'
        verbose_name_plural = verbose_name
