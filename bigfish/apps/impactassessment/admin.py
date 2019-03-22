from django.contrib import admin

from bigfish.apps.impactassessment.models import KlassWeekData, StudentWeekData, StudentMonthData, KlassMonthData
from bigfish.utils.functions import format_admin_list


@admin.register(StudentWeekData)
class StudentWeekDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(StudentWeekData)
    list_filter = ['term_id']
    save_as = True
    # list_editable = format_admin_list(StudentWeekData, remove=['id', 'create_time', 'update_time'])


@admin.register(KlassWeekData)
class KlassWeekDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(KlassWeekData)
    list_filter = ['term_id']
    # list_editable = format_admin_list(KlassWeekData, remove=['id'])


@admin.register(StudentMonthData)
class StudentMonthDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(StudentMonthData)
    save_as = True
    # list_editable = format_admin_list(StudentWeekData,
    #                                   remove=['id', 'create_time', 'update_time', 'term', 'school_week', 'term_week'])


@admin.register(KlassMonthData)
class KlassMonthDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(KlassMonthData)
    list_filter = ['term_id']
    save_as = True
    # list_editable = format_admin_list(KlassMonthData, remove=['id'])
