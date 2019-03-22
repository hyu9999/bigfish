from django.db import models

from bigfish.apps.impactassessment.abs_models import AbsComputeData, AbsFilterData
from bigfish.apps.schools.models import TermWeek, SchoolWeek, Term
from bigfish.apps.visualbackend.abs_models import AbsProvince, AbsCity, AbsDistrict, AbsSchool, AbsKlass, AbsUserBelong


# ----------------------学周数据
class StudentWeekData(AbsSchool, AbsKlass, AbsUserBelong, AbsComputeData):
    term = models.ForeignKey(Term,
                             on_delete=models.CASCADE,
                             verbose_name="学期",
                             blank=True, null=True,
                             related_name="%(app_label)s_%(class)s_term")
    term_week = models.ForeignKey(TermWeek,
                                  on_delete=models.CASCADE,
                                  verbose_name="学周",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_week")
    school_week = models.ForeignKey(SchoolWeek,
                                    on_delete=models.CASCADE,
                                    verbose_name="学校学周",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_school_week")

    class Meta:
        verbose_name = "学生学周数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}]{}".format(self.school_week.title, self.username)


class KlassWeekData(AbsProvince, AbsCity, AbsDistrict, AbsSchool, AbsKlass, AbsFilterData, AbsComputeData):
    term_week = models.ForeignKey(TermWeek,
                                  on_delete=models.CASCADE,
                                  verbose_name="学周",
                                  blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_week")
    school_week = models.ForeignKey(SchoolWeek,
                                    on_delete=models.CASCADE,
                                    verbose_name="学校学周",
                                    blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_school_week")

    class Meta:
        verbose_name = "班级数据(week)"
        verbose_name_plural = verbose_name


# ----------------------月度数据
MONTH_CHOICE = (
    (1, "1月"),
    (2, "2月"),
    (3, "3月"),
    (4, "4月"),
    (5, "5月"),
    (6, "6月"),
    (7, "7月"),
    (8, "8月"),
    (9, "9月"),
    (10, "10月"),
    (11, "11月"),
    (12, "12月"),
)


class StudentMonthData(AbsSchool, AbsKlass, AbsUserBelong, AbsComputeData):
    school_year = models.IntegerField("年份", blank=True, default=2018)
    school_month = models.IntegerField("月份", choices=MONTH_CHOICE, default=1)

    class Meta:
        verbose_name = "学生每月数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[{}{}]{}".format(self.school_year, self.school_month, self.username)


class KlassMonthData(AbsProvince, AbsCity, AbsDistrict, AbsSchool, AbsKlass, AbsFilterData, AbsComputeData):
    school_year = models.IntegerField("年份", blank=True, default=2018)
    school_month = models.IntegerField("月份", choices=MONTH_CHOICE, default=1)

    class Meta:
        verbose_name = "班级数据(month)"
        verbose_name_plural = verbose_name
