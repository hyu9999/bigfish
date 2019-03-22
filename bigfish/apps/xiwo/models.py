from django.conf import settings
from django.db import models
from django.utils import timezone

from bigfish.base.choices import BIND_STATUS


class SerialLevel(models.Model):
    name = models.CharField("名称", max_length=100)
    level = models.PositiveIntegerField("级别", default=0)
    effect_duration = models.PositiveIntegerField("有效时长", blank=True, default=0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "序列号级别"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.name)


class SerialNum(models.Model):
    # 规则： 年（2位）+月（2位）+随机数（5位）
    serial_num = models.IntegerField("序列号", unique=True)
    encrypted_serial = models.CharField("加密序列", max_length=100, blank=True, default="")
    level = models.ForeignKey(SerialLevel,
                              on_delete=models.CASCADE,
                              verbose_name="序列号级别",
                              blank=True, null=True,
                              related_name="%(app_label)s_%(class)s_level")
    max_times = models.PositiveIntegerField("最大更换次数", blank=True, default=0)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "序列号"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.level.name, self.serial_num)


class SerialBindingRelation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name="用户",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_user")
    serial_num = models.OneToOneField(SerialNum,
                                      on_delete=models.CASCADE,
                                      verbose_name="序列号",
                                      related_name="%(app_label)s_%(class)s_serial_num")
    device_code = models.CharField("绑定设备码", max_length=100, blank=True, default="")
    bind_status = models.IntegerField("绑定状态", choices=BIND_STATUS, default=1)
    bind_time = models.DateTimeField("绑定时间", default=timezone.now)
    invalid_time = models.DateTimeField("失效时间", default=timezone.now)
    change_times = models.PositiveIntegerField("设备更换次数", blank=True, default=0)
    is_normal = models.BooleanField("是否正式使用", default=False)

    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "序列号绑定关系"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.serial_num)


class SerialBindingReport(models.Model):
    serial_num = models.IntegerField("序列号")
    device_code = models.CharField("新设备码", max_length=100, blank=True, default="")
    old_device_code = models.CharField("旧设备码", max_length=100, blank=True, default="")
    bind_time = models.DateTimeField("绑定时间", default=timezone.now)
    invalid_time = models.DateTimeField("失效时间", default=timezone.now)
    change_times = models.PositiveIntegerField("设备更换次数", blank=True, default=0)
    remark = models.TextField("备注信息", blank=True, default="")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "序列号绑定记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.serial_num)
