from django.db import models


class AbsModel(models.Model):
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # create_time = models.DateTimeField("创建时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    # update_time = models.DateTimeField("更新时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))

    class Meta:
        abstract = True


class AbsUserBelong(models.Model):
    in_use = models.BooleanField("是否使用", default=False)  # 该学生本学期是否使用过APP
    district_code = models.IntegerField("区县编码", default=0)
    province = models.CharField("省份", max_length=200, blank=True, default="")
    city = models.CharField("城市", max_length=200, blank=True, default="")
    district = models.CharField("区县", max_length=200, blank=True, default="")
    username = models.CharField("账户", max_length=200, blank=True, default="")
    description = models.TextField("描述", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # create_time = models.DateTimeField("创建时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))
    # update_time = models.DateTimeField("更新时间", default=datetime.datetime.strptime(
    #     '2017-10-09 00:00:00','%Y-%m-%d %H:%M:%S'))

    class Meta:
        abstract = True


class AbsLesson(models.Model):
    lesson_id = models.IntegerField("课程ID", default=0, db_index=True)
    lesson_title = models.CharField("课程名称", max_length=200, blank=True, default="")
    lesson_order = models.CharField("课程名称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True


class AbsUnit(models.Model):
    publish_id = models.IntegerField("教材ID", default=0, db_index=True)
    publish_name = models.CharField("教材名称", max_length=200, blank=True, default="")
    unit_id = models.IntegerField("单元ID", default=0, db_index=True)
    unit_title = models.CharField("单元名称", max_length=200, blank=True, default="")
    unit_num = models.PositiveIntegerField('单元编号', null=True, blank=True)

    class Meta:
        abstract = True


class AbsKlass(models.Model):
    klass_id = models.IntegerField("班级ID", default=0, db_index=True)
    klass_name = models.CharField("班级名称", max_length=200, blank=True, default="")
    grade_name = models.CharField("年级", max_length=200, blank=True, default="")
    klass_order = models.PositiveIntegerField("序号", null=True, blank=True, default=0)

    class Meta:
        abstract = True


class AbsSchool(models.Model):
    school_id = models.IntegerField("学校ID", default=0, db_index=True)
    school_name = models.CharField("学校名称", max_length=200, blank=True, default="")
    short_name = models.CharField("学校简称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True


class AbsDistrict(models.Model):
    district_code = models.IntegerField("区县码", default=0, db_index=True)
    district_name = models.CharField("区县名称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True


class AbsCity(models.Model):
    city_code = models.IntegerField("城市码", default=0, db_index=True)
    city_name = models.CharField("城市名称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True


class AbsProvince(models.Model):
    province_code = models.IntegerField("省份码", default=0, db_index=True)
    province_name = models.CharField("省份名称", max_length=200, blank=True, default="")

    class Meta:
        abstract = True
