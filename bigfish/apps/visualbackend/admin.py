from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from bigfish.apps.visualbackend.models import StudentData, TeacherData, StageScore, \
    ExaminationCondition
from bigfish.utils.functions import format_admin_list, format_admin_search_fields


class StageScoreResource(resources.ModelResource):
    class Meta:
        model = StageScore


@admin.register(StageScore)
class StageScoreAdmin(ImportExportModelAdmin):
    resource_class = StageScoreResource
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(StageScore)


@admin.register(StudentData)
class StudentDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(StudentData,
                                     remove=['school_name', 'grade', 'short_name'])
    search_fields = format_admin_search_fields(StudentData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']


@admin.register(TeacherData)
class TeacherDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(TeacherData)
    search_fields = format_admin_search_fields(TeacherData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']


@admin.register(ExaminationCondition)
class ExaminationConditionAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(ExaminationCondition)
