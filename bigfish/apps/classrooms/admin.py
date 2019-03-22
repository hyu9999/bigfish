from django.contrib import admin

from bigfish.apps.classrooms.models import Classroom, ActivityReport, ActivityDetailReport, \
    BlackSetting, BlackSettingReport, Cast, CastReport, StuActivity
from bigfish.utils.functions import format_admin_list


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Cast)


@admin.register(CastReport)
class CastReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(CastReport)


@admin.register(BlackSetting)
class BlackSettingAdmin(admin.ModelAdmin):
    list_display = format_admin_list(BlackSetting)


@admin.register(BlackSettingReport)
class BlackSettingReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(BlackSettingReport)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Classroom)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title')
    list_filter = ('is_active', 'is_open', 'is_prepare', 'identity')
    show_full_result_count = False


@admin.register(StuActivity)
class StuActivityAdmin(admin.ModelAdmin):
    list_display = format_admin_list(StuActivity)
    raw_id_fields = ('user', 'classroom', 'unit', 'lesson', 'activity',)
    date_hierarchy = 'start_time'
    search_fields = (
        'id', 'school_name', 'klass_name', 'unit_name', 'lesson_name', 'act_title', 'username')
    list_filter = ('is_finish', 'is_complete', 'is_push')
    show_full_result_count = False


@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ActivityReport)
    raw_id_fields = ('user', 'classroom', 'unit', 'lesson', 'activity',)
    date_hierarchy = 'start_time'
    search_fields = (
        'id', 'school_name', 'klass_name', 'unit_name', 'lesson_name', 'act_title', 'username')
    list_filter = ('is_complete', 'is_push')
    show_full_result_count = False


@admin.register(ActivityDetailReport)
class ActivityDetailReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ActivityDetailReport)
    raw_id_fields = ('user', 'classroom', 'unit', 'lesson', 'activity',)
    date_hierarchy = 'start_time'
    search_fields = (
        'id', 'school_name', 'klass_name', 'unit_name', 'lesson_name', 'act_title', 'username')
    list_filter = ('is_complete', 'is_push')
    show_full_result_count = False
