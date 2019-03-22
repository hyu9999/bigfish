from django.contrib import admin

from bigfish.apps.homework.models import Homework, PushRecord, ReceiveRecord, HomeworkRecord, HomeworkDetailRecord, \
    HomeworkClick
from bigfish.utils.functions import format_admin_list


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Homework)


@admin.register(PushRecord)
class PushRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(PushRecord)


@admin.register(ReceiveRecord)
class ReceiveRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ReceiveRecord)


@admin.register(HomeworkRecord)
class HomeworkRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(HomeworkRecord)


@admin.register(HomeworkDetailRecord)
class HomeworkDetailRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(HomeworkDetailRecord)


@admin.register(HomeworkClick)
class HomeworkClickAdmin(admin.ModelAdmin):
    list_display = format_admin_list(HomeworkClick)
