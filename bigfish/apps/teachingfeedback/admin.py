from django.contrib import admin

from bigfish.apps.teachingfeedback.models import ActivityData, LessonData, TestReview, UnitData, \
    UnitTestData
from bigfish.utils.functions import format_admin_list


@admin.register(ActivityData)
class ActivityDataAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ActivityData)
    date_hierarchy = 'update_time'


@admin.register(LessonData)
class LessonDataAdmin(admin.ModelAdmin):
    list_display = format_admin_list(LessonData)
    date_hierarchy = 'update_time'


@admin.register(TestReview)
class TestReviewAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TestReview)
    date_hierarchy = 'update_time'


@admin.register(UnitData)
class UnitDataAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UnitData)
    date_hierarchy = 'update_time'


@admin.register(UnitTestData)
class UnitTestDataAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UnitTestData)
    date_hierarchy = 'update_time'
