import jsonfield
import os

from django.conf import settings
from django.db import models

MEDIA_PREFIX = 'bfwechat'


def media_directory(instance, filename):
    path = os.path.join(MEDIA_PREFIX)
    if isinstance(instance, MediaSource):
        path = os.path.join(path, 'mediasource')
    else:
        path = os.path.join(path, 'unknown-{}'.format(instance.pk))
    path = os.path.join(path, filename)
    return path


class WxUser(models.Model):
    SEX_CHOICE = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )
    ROLE_CHOICE = (
        (0, "管理员"),
        (1, "家长"),
        (2, "学生"),
    )

    username = models.CharField("账号", max_length=150)
    student = models.ManyToManyField(settings.AUTH_USER_MODEL, through='WxUserRelationship')
    openid = models.CharField("微信唯一标识", max_length=150)
    password = models.CharField("密码", max_length=150, default="123456", blank=True)
    nickname = models.CharField("昵称", max_length=150, default="")
    sex = models.IntegerField("性别", choices=SEX_CHOICE, default=0)
    phone_num = models.CharField("电话", max_length=30, default="", blank=True)
    email = models.EmailField("邮件地址", blank=True)
    area = jsonfield.JSONField("所在地区", default={}, blank=True)
    role = models.IntegerField("身份", choices=ROLE_CHOICE, default=1)
    head_img = models.CharField("头像", max_length=500, default="", blank=True)
    unionid = models.CharField("唯一标识", max_length=150)
    is_active = models.BooleanField("是否活跃", default=False)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "微信用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.username, self.unionid)


class ActiveToken(models.Model):
    token = models.CharField("token", max_length=300)
    app_id = models.CharField("APPID", max_length=300)
    app_secret = models.CharField("APPSECRET", max_length=300)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "Token记录表"
        verbose_name_plural = verbose_name


class MediaSource(models.Model):
    MEDIA_TYPE_CHOICE = (
        ("image", "图片"),  # 2M，支持PNG\JPEG\JPG\GIF格式
        ("voice", "语音"),  # 2M，播放长度不超过60s，支持AMR\MP3格式
        ("video", "视频"),  # 10MB，支持MP4格式
        ("thumb", "缩略图"),  # 64KB，支持JPG格式
    )

    title = models.CharField("标题", max_length=200, default="")
    media_type = models.CharField("媒体类型", max_length=200, choices=MEDIA_TYPE_CHOICE, default="image")
    url = models.URLField("资源路径", default="")
    update_time = models.DateTimeField("更新时间", auto_now=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "多媒体资源表"
        verbose_name_plural = verbose_name


class KeyWord(models.Model):
    CONTENT_TYPE_CHOICE = (
        ("text", "文本"),
        ("image", "图片"),
        ("voice", "语音"),
        ("video", "视频"),
        ("shortvideo", "小视频"),
        ("location", "地理位置"),
        ("link", "链接"),
    )
    title = models.CharField("名称", max_length=200)
    content = models.CharField("内容", max_length=200)
    content_type = models.CharField("消息类型", max_length=200, choices=CONTENT_TYPE_CHOICE, default="text")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        unique_together = ('title', 'content_type')
        verbose_name = "查询关键词表"
        verbose_name_plural = verbose_name


class SendMsg(models.Model):
    MSG_TYPE_CHOICE = (
        ("text", "文本"),
        ("image", "图片"),
        ("voice", "语音"),
        ("video", "视频"),
        ("music", "音乐"),
        ("article", "图文"),
        ("news", "永久素材的图文"),
        ("event", "事件"),
    )
    title = models.CharField("名称", max_length=200)
    msg_type = models.CharField("类型", max_length=200, choices=MSG_TYPE_CHOICE, default="text")
    content = models.TextField("发送内容")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "发送内容表"
        verbose_name_plural = verbose_name


class TemplateMsg(models.Model):
    title = models.CharField("标题", max_length=200)
    primary_industry = models.CharField("一级行业", max_length=200, default="")
    deputy_industry = models.CharField("二级行业", max_length=200, default="")
    template_id = models.CharField("模板ID", max_length=200, default="")
    template_id_short = models.CharField("模板编号", max_length=200, blank=True, default="")
    content = jsonfield.JSONField("模板内容", default={})
    example = models.TextField("模板示例", default="")

    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "模板信息表"
        verbose_name_plural = verbose_name


class TemplateMsgRecord(models.Model):
    title = models.CharField("标题", max_length=200, default="")
    message_id = models.CharField("信息id", max_length=200, default="")
    data = jsonfield.JSONField("模板数据", default={})
    url = models.URLField("模板跳转链接", default="")
    template_id = models.CharField("模板id", max_length=200, blank=True, default="")
    from_user = models.IntegerField("发送人", default=0)
    to_user = models.CharField("接收者openid", max_length=200, default="")
    mini_program = jsonfield.JSONField("跳小程序所需数据", default={})
    if_success = models.BooleanField("是否发送成功", default=True)
    error_msg = models.TextField("错误信息", default="")

    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "模板信息记录表"
        verbose_name_plural = verbose_name


class WxArticleMsg(models.Model):
    title = models.CharField("名称", max_length=200)
    media_id = models.CharField("图文的媒体ID", max_length=200, default="")
    content = jsonfield.JSONField("详细内容", default={})
    example = models.TextField("内容示例", default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "图文信息"
        verbose_name_plural = verbose_name


class WxArticleMsgRecord(models.Model):
    title = models.CharField("名称", max_length=200)
    media_id = models.CharField("图文的媒体ID", max_length=200, default="")
    receiver = jsonfield.JSONField("接收人", default={})
    content = jsonfield.JSONField("发送内容", default={})
    receive_msg = jsonfield.JSONField("返回信息", default={})
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "图文信息记录"
        verbose_name_plural = verbose_name


class WxUserRelationship(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                verbose_name="学生",
                                related_name="%(app_label)s_%(class)s_student"
                                )
    wx_user = models.ForeignKey(WxUser, on_delete=models.CASCADE,
                                verbose_name="微信用户",
                                related_name="%(app_label)s_%(class)s_wx_user"
                                )
    is_active = models.BooleanField("是否有效", default=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    relationship = models.CharField("关系", max_length=150, default="", blank=True)
    remark = models.TextField("备注", default="", blank=True)

    class Meta:
        verbose_name = "微信用户关联关系"
        verbose_name_plural = verbose_name


class Feedback(models.Model):
    wx_user = models.ForeignKey(WxUser, on_delete=models.CASCADE,
                                verbose_name="微信用户",
                                related_name="%(app_label)s_%(class)s_wx_user"
                                )
    content = models.TextField("反馈内容", default="")
    phone = models.IntegerField("联系方式", default=0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "意见反馈"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.content)


def wx_banner_image(instance, filename):
    return os.path.join(
        'banner',
        filename
    )


class WxBanner(models.Model):
    add_time = models.DateTimeField("添加时间", auto_now_add=True)
    image = models.FileField(upload_to=wx_banner_image)
    is_active = models.BooleanField('是否有效', default=True)

    class Meta:
        verbose_name = "微信首页轮播图"
        verbose_name_plural = verbose_name
