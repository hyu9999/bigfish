from django.contrib import admin

from bigfish.apps.reports.models import ExaminationReport, \
    RatingReport, PracticalCourseRecord, StudentDailyData, KlassDailyData, SchoolDailyData, ActivityDailyData
from bigfish.utils.functions import generate_fields


@admin.register(ExaminationReport)
class ExaminationReportAdmin(admin.ModelAdmin):
    list_display = generate_fields(ExaminationReport)
    list_filter = ('school_code', 'academic_year',)
    search_fields = ('academic_year', 'term', 'school_code', 'grade', 'username', 'realname',)


@admin.register(RatingReport)
class RatingReportAdmin(admin.ModelAdmin):
    list_display = generate_fields(RatingReport)
    list_filter = ('school_code', 'academic_year',)
    search_fields = ('academic_year', 'term', 'school_code', 'grade', 'username', 'realname',)


@admin.register(PracticalCourseRecord)
class PracticalCourseRecordAdmin(admin.ModelAdmin):
    list_display = generate_fields(PracticalCourseRecord)
    search_fields = ('subject', 'schedule', 'teaching_date')
    date_hierarchy = 'add_time'


@admin.register(StudentDailyData)
class StudentDailyDataAdmin(admin.ModelAdmin):
    list_display = generate_fields(StudentDailyData)
    search_fields = ('student__username', 'record_date')
    date_hierarchy = 'add_time'


@admin.register(KlassDailyData)
class KlassDailyDataAdmin(admin.ModelAdmin):
    list_display = generate_fields(KlassDailyData)
    search_fields = ('klass__name', 'klass__grade', 'klass__school__name', 'record_date')
    date_hierarchy = 'add_time'


@admin.register(SchoolDailyData)
class SchoolDailyDataAdmin(admin.ModelAdmin):
    list_display = generate_fields(SchoolDailyData)
    search_fields = ('school__name', 'record_date')
    date_hierarchy = 'add_time'


@admin.register(ActivityDailyData)
class ActivityDailyDataAdmin(admin.ModelAdmin):
    list_display = generate_fields(ActivityDailyData)
    search_fields = ('school_name', 'klass_name', 'act_type_name', 'record_date')
    date_hierarchy = 'add_time'
