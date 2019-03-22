from django.db import models

from bigfish.apps.overall.abs_models import AbsStdData, AbsOverallData, AbsStageScore
from bigfish.apps.schools.models import Term
from bigfish.apps.visualbackend.abs_models import AbsProvince, AbsCity, AbsDistrict, AbsSchool, AbsKlass


class KlassData(AbsDistrict, AbsSchool, AbsKlass, AbsStdData, AbsOverallData, AbsStageScore):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name = "班级数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "班级总体数据:{}".format(self.klass_name)


class SchoolData(AbsDistrict, AbsSchool, AbsStdData, AbsOverallData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name = "学校数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "学校总体数据:{}".format(self.school_name)


class DistrictData(AbsProvince, AbsCity, AbsDistrict, AbsStdData, AbsOverallData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name = "区县数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "区县总体数据:{}".format(self.district_name)


class CityData(AbsProvince, AbsCity, AbsStdData, AbsOverallData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name = "城市数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "城市总体数据:{}".format(self.city_name)


class ProvinceData(AbsProvince, AbsStdData, AbsOverallData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")

    class Meta:
        verbose_name = "省份数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "省份总体数据:{}".format(self.province_name)
