import os

import jsonfield
from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.apps.areas.models import Area
from bigfish.apps.schools.models import School, Klass
from bigfish.apps.users.models import BigfishUser
from bigfish.base.models import AbsClick

DUBBING_DIR = 'dubbing'


def dubbing_media(instance, filename):
    if isinstance(instance, DubbingSRC):
        path = os.path.join(
            DUBBING_DIR,
            'base',
            filename
        )
    elif isinstance(instance, UserDubbing):
        path = os.path.join(
            DUBBING_DIR,
            'user-source',
            filename
        )
    elif isinstance(instance, DubbingCategory):
        path = os.path.join(
            DUBBING_DIR,
            'dubbing_category',
            filename
        )
    else:
        path = os.path.join(DUBBING_DIR, 'unknown', filename)
    return path


def dubbing_video(instance, filename):
    base_dir = os.path.dirname(dubbing_media(instance, filename))
    path = os.path.join(base_dir, 'video', filename)
    return path


def dubbing_audio(instance, filename):
    base_dir = os.path.dirname(dubbing_media(instance, filename))
    path = os.path.join(base_dir, 'audio', filename)
    return path


def dubbing_img(instance, filename):
    base_dir = os.path.dirname(dubbing_media(instance, filename))
    path = os.path.join(base_dir, 'img', filename)
    return path


class AbsDubbing(models.Model):
    description = models.TextField("描述", blank=True, null=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True


class DubbingMain(AbsDubbing):
    name = models.CharField("名称", max_length=200)
    image = models.ImageField("图片", upload_to=dubbing_media, blank=True, null=True)
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    is_default = models.BooleanField("默认分类", default=False)

    class Meta:
        verbose_name_plural = '趣配音主分类'

    def __str__(self):
        return self.name


class DubbingCategory(AbsDubbing):
    name = models.CharField("名称", max_length=200)
    image = models.ImageField("图片", upload_to=dubbing_media, blank=True, null=True)
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_active = models.BooleanField("是否有效", default=True)
    is_default = models.BooleanField("默认分类", default=False)
    dubbing_main = models.ForeignKey(DubbingMain,
                                     verbose_name="趣配音主分类",
                                     related_name="%(app_label)s_%(class)s_dubbing_main",
                                     blank=True, null=True)

    class Meta:
        verbose_name_plural = '趣配音二级分类'

    def __str__(self):
        return self.name


class DubbingSRC(AbsDubbing):
    video = models.FileField("视频", upload_to=dubbing_media, blank=True)
    audio = models.FileField("音频", upload_to=dubbing_media, blank=True)
    image = models.ImageField("图片", upload_to=dubbing_media, blank=True)
    stop_image = models.ImageField("暂停图片", upload_to=dubbing_media, blank=True)
    dialogue = jsonfield.JSONField("字幕", default={})
    dubbing_category = models.ForeignKey(DubbingCategory,
                                         verbose_name="趣配音二级分类",
                                         related_name="%(app_label)s_%(class)s_dubbing_category",
                                         blank=True, null=True)
    """
    学分规则
    {
        "first":{
            
        },
        "second":{
            "basic":{
                "total":40,
                "single":5
            }
        },
        "third":{
            "basic":{
                "total":13,
                "single":4
            }
        },
        "forth":{
            "basic":{
                "total":80,
                "single":27
            }
        }
    }
    """
    score_rule = jsonfield.JSONField('学分规则', default={})
    click_num = models.PositiveIntegerField("点击数", default=0)
    is_lesson = models.BooleanField("是否课程中", default=False)
    is_active = models.BooleanField("是否有效", default=True)
    is_banner = models.BooleanField("是否滚动横幅", default=False)
    grouping = models.CharField("类别分组", max_length=500, blank=True, default="")
    order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)
    is_competition = models.BooleanField("是否参赛作品", default=False)

    class Meta:
        verbose_name_plural = '趣配音'

    def __str__(self):
        if self.is_competition is True:
            ret_str = "[赛]{} {}".format(self.grouping, self.description)
        else:
            ret_str = "{} {}".format(self.grouping, self.description)
        return ret_str


class CompetitionImg(models.Model):
    IMG_TYPE_CHOICE = (
        (1, '宣传Banner'),
        (2, '结果好Banner'),
        (3, '结果差Banner'),
    )
    title = models.CharField("名称", max_length=200, default="")
    img_type = models.IntegerField("类型", choices=IMG_TYPE_CHOICE, default=1)
    img = models.ImageField("图片", upload_to=dubbing_media, blank=True)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "配音大赛图片"

    def __str__(self):
        return "{}".format(self.title)


class Competition(models.Model):
    CATEGORY_CHOICE = (
        (1, "全服"),
        (2, "地区"),
        (3, "年级"),
        (4, "其他"),
    )
    title = models.CharField("主题", max_length=300, default="",
                             help_text="主题")
    content = models.TextField("奖励设置", default="", help_text="奖励设置")
    notice = models.TextField("参赛须知", default="", help_text="参赛须知")
    banner = models.ManyToManyField(CompetitionImg,
                                    through='CompetitionImgRelationship',
                                    help_text="banner图")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="发起人",
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True, help_text="发起人")
    start_date = models.DateField("开始日期", default=timezone.now, help_text="开始日期")
    end_date = models.DateField("截止日期", default=timezone.now, help_text="截止日期")
    order = models.PositiveIntegerField("序号", default=0, help_text="序号")
    category = models.IntegerField("分类", choices=CATEGORY_CHOICE, default=1, help_text="分类")
    is_active = models.BooleanField("是否有效", default=True, help_text="是否有效")
    is_settle = models.BooleanField("是否结算", default=False, help_text="是否结算")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = '配音大赛'

    def __str__(self):
        return "【第{}届配音大赛】{}".format(self.order, self.title)


class CompetitionImgRelationship(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE,
                                    verbose_name="配音大赛",
                                    related_name="%(app_label)s_%(class)s_competition",
                                    help_text="配音大赛"
                                    )
    banner = models.ForeignKey(CompetitionImg, on_delete=models.CASCADE,
                               verbose_name="banner图",
                               related_name="%(app_label)s_%(class)s_wx_banner",
                               help_text="banner图"
                               )
    add_time = models.DateTimeField("添加时间", auto_now_add=True, help_text="添加时间")
    order = models.PositiveIntegerField("排序", default=1, help_text="排序")
    remark = models.TextField("备注", default="", blank=True, help_text="备注")

    class Meta:
        verbose_name = "配音大赛轮播图关系"
        verbose_name_plural = verbose_name


class AreaCompetition(models.Model):
    CATEGORY_CHOICE = (
        (0, "未知"),
        (1, "学校"),
        (2, "班级"),
    )
    competition = models.ForeignKey(Competition,
                                    verbose_name="配音大赛",
                                    related_name="%(app_label)s_%(class)s_competition",
                                    blank=True, null=True,
                                    help_text="配音大赛")
    area = models.ForeignKey(Area,
                             verbose_name="区域",
                             related_name="%(app_label)s_%(class)s_area",
                             blank=True, null=True,
                             help_text="区域")
    category = models.IntegerField("分类", choices=CATEGORY_CHOICE, default=0, help_text="分类")

    class Meta:
        verbose_name = "各分区配音大赛"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} {}".format(self.competition.title, self.get_category_display(), )


class SubCompetition(models.Model):
    GRADE_CHOICES = (
        (0, "未知"),
        (11, "小学一年级"),
        (12, "小学二年级"),
        (13, "小学三年级"),
        (14, "小学四年级"),
        (15, "小学五年级"),
        (16, "小学六年级"),
        (21, "初中一年级"),
        (22, "初中二年级"),
        (23, "初中三年级"),
        (31, "高中一年级"),
        (32, "高中二年级"),
        (33, "高中三年级")
    )
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE,
                                    verbose_name="配音大赛",
                                    related_name="%(app_label)s_%(class)s_competition",
                                    blank=True, null=True,
                                    help_text="配音大赛"
                                    )
    area_competition = models.ForeignKey(AreaCompetition,
                                         verbose_name="分区配音大赛",
                                         related_name="%(app_label)s_%(class)s_area_competition",
                                         blank=True, null=True,
                                         help_text="分区配音大赛")
    area = models.ForeignKey(Area,
                             verbose_name="区域",
                             related_name="%(app_label)s_%(class)s_area",
                             blank=True, null=True,
                             help_text="区域")
    school = models.ForeignKey(School,
                               verbose_name="学校",
                               related_name="%(app_label)s_%(class)s_school",
                               blank=True, null=True,
                               help_text="学校")
    grade = models.IntegerField("年级", choices=GRADE_CHOICES, default=0, help_text="年级")
    klass = models.ForeignKey(Klass,
                              verbose_name="班级",
                              related_name="%(app_label)s_%(class)s_klass",
                              blank=True, null=True,
                              help_text="班级")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="添加人",
                             related_name="%(app_label)s_%(class)s_user",
                             blank=True, null=True,
                             help_text="添加人")
    dubbingsrc = models.ManyToManyField(DubbingSRC,
                                        related_name='%(app_label)s_%(class)s_dubbingsrc',
                                        verbose_name='配音资源',
                                        help_text="配音资源")
    prepare_time = models.DateTimeField("准备时间", default=timezone.now, help_text="准备时间")
    competing_time = models.DateTimeField("比赛时间", default=timezone.now, help_text="比赛时间")
    end_time = models.DateTimeField("比赛结束时间", default=timezone.now, help_text="比赛结束时间")
    is_active = models.BooleanField("是否有效", default=True, help_text="是否有效")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = '配音大赛分赛区'

    def __str__(self):
        if self.klass is not None:
            ret_str = "{}[{}{}{}{}]".format(self.competition.title, self.area, self.school, self.get_grade_display(),
                                            self.klass)
        elif self.grade != 0:
            ret_str = "{}[{}{}]".format(self.competition.title, self.area, self.school, self.get_grade_display())
        elif self.school is not None:
            ret_str = "{}[{}{}]".format(self.competition.title, self.area, self.school)
        elif self.area is not None:
            ret_str = "{}[{}]".format(self.competition.title, self.area)
        else:
            ret_str = "{}".format(self.competition.title)
        return ret_str


class UserDubbing(AbsDubbing):
    video = models.FileField("视频", upload_to=dubbing_media, blank=True)
    audio = models.FileField("音频", upload_to=dubbing_media, blank=True)
    image = models.ImageField("图片", upload_to=dubbing_media, blank=True)
    total_time = models.FloatField("总用时", default=0.0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             related_name="%(app_label)s_%(class)s_user")
    dubbingsrc = models.ForeignKey(DubbingSRC,
                                   on_delete=models.CASCADE,
                                   verbose_name="趣配音资源",
                                   related_name="%(app_label)s_%(class)s_dubbingsrc")
    is_public = models.BooleanField("是否公开", default=True)
    # TODO 旧区域
    area = models.IntegerField("区域码", default=0, blank=True)
    video_url = models.CharField("视频地址", max_length=500, blank=True, default="")
    is_shared = models.BooleanField("是否分享", default=False)
    """
    阶段：
    {
        "first_stage":0,
        "second_stage":0,
        "third_stage":0,
        "forth_stage":0
    }
    """
    stage = jsonfield.JSONField('阶段', default={})
    sub_competition = models.ForeignKey(SubCompetition,
                                        on_delete=models.CASCADE,
                                        verbose_name="配音大赛分赛区",
                                        related_name="%(app_label)s_%(class)s_sub_competition",
                                        blank=True, null=True)
    is_competition = models.BooleanField("是否参赛作品", default=False)
    is_active = models.BooleanField("是否有效", default=True, blank=True)
    zan_num = models.IntegerField("点赞数", blank=True, default=0)

    class Meta:
        verbose_name_plural = '用户配音作品'

    def __str__(self):
        if self.is_competition:
            return "{} [参赛作品] [{}-{}]".format(self.description, self.user.username, self.create_time)
        else:
            return "{} [{}-{}]".format(self.description, self.user.username, self.create_time)


class CompetitionRank(models.Model):
    competition = models.ForeignKey(Competition,
                                    verbose_name="配音大赛",
                                    related_name="%(app_label)s_%(class)s_competition",
                                    help_text="配音大赛")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="选手",
                             related_name="%(app_label)s_%(class)s_user",
                             help_text="选手")
    realname = models.CharField("姓名", max_length=200, default="", blank=True, help_text="姓名")
    # TODO 旧区域
    area_id = models.PositiveIntegerField("所在地区码", default=0, help_text="所在地区id")
    school_id = models.PositiveIntegerField("所在学校id", default=0, help_text="所在学校id")
    class_id = models.PositiveIntegerField("所在班级id", default=0, help_text="所在班级id")
    # TODO 旧区域
    area = models.CharField("所在地区码", max_length=200, default="", blank=True, help_text="所在地区码")
    school = models.CharField("所在学校", max_length=200, default="", blank=True, help_text="所在学校")
    klass = models.CharField("所在班级", max_length=200, default="", blank=True, help_text="所在班级")
    user_dubbing = models.ForeignKey(UserDubbing,
                                     verbose_name="作品",
                                     related_name="%(app_label)s_%(class)s_user_dubbing",
                                     help_text="作品")
    rank = models.PositiveIntegerField("排名", default=0, help_text="排名")
    is_receive_award = models.BooleanField("是否领取奖励", default=False, help_text="是否领取奖励")
    bf_coin = models.PositiveIntegerField("获得大渔币数量", default=0, help_text="获得大渔币数量")
    zan_num = models.PositiveIntegerField("点赞数", default=0, help_text="点赞数")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name_plural = "配音大赛排行榜"
        ordering = ['rank']

    def __str__(self):
        return "[{}]{}_第{}名".format(self.competition.title, self.user.username, self.rank)


class RewardConfig(models.Model):
    competition = models.ForeignKey(Competition,
                                    verbose_name="配音大赛",
                                    related_name="%(app_label)s_%(class)s_competition",
                                    help_text="配音大赛")
    """
    {
        "ranking_reward":[
                            {"ranking":1, "reward":2000},
                            {"ranking":2, "reward":1000},
                        ],
        "participation_reward":100
    }
    """
    reward_data = jsonfield.JSONField("奖励配置", blank=True, null=True, default={})

    class Meta:
        verbose_name_plural = "配音大赛奖励配置"

    def __str__(self):
        return "[{}]奖励配置".format(self.competition.title)


class DubbingClick(AbsClick):
    user = models.ForeignKey(BigfishUser,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_用户")
    dubbingsrc = models.ForeignKey(DubbingSRC,
                                   on_delete=models.CASCADE,
                                   verbose_name="趣配音资源",
                                   related_name="%(app_label)s_%(class)s_dubbingsrc")

    class Meta:
        verbose_name_plural = '用户点击趣配音记录'

    def __str__(self):
        return "{}[{}]".format(self.dubbingsrc.description, self.user.username)


class DubbingZan(AbsDubbing):
    userdubbing = models.ForeignKey(UserDubbing,
                                    on_delete=models.CASCADE,
                                    verbose_name="用户配音",
                                    related_name="%(app_label)s_%(class)s_userdubbing")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="点赞人",
                             related_name="%(app_label)s_%(class)s_user")
    zan_num = models.PositiveIntegerField("点赞数", blank=True, default=0)

    class Meta:
        unique_together = ('userdubbing', 'user')
        verbose_name_plural = '用户点赞记录'

    def __str__(self):
        return "{}".format(self.description)


class DubbingRead(AbsDubbing):
    userdubbing = models.ForeignKey(UserDubbing,
                                    on_delete=models.CASCADE,
                                    verbose_name="配音作品",
                                    related_name="%(app_label)s_%(class)s_userdubbing")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="粉丝",
                             related_name="%(app_label)s_%(class)s_user")
    is_read = models.BooleanField("是被更新过", default=False)

    class Meta:
        verbose_name_plural = '用户关注圈记录'

    def __str__(self):
        return "{}".format(self.description)
