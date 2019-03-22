from django.contrib import admin

from bigfish.apps.operation.models import OperateType, Operation, OperationRecord, ActClick
from bigfish.utils.functions import format_admin_list


@admin.register(OperateType)
class OperateTypeAdmin(admin.ModelAdmin):
    list_display = format_admin_list(OperateType)


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Operation)


@admin.register(OperationRecord)
class OperationRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(OperationRecord)


@admin.register(ActClick)
class ActClickAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ActClick)
