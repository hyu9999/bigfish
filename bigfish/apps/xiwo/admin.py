from django.contrib import admin

from bigfish.apps.xiwo.models import SerialBindingRelation, SerialLevel, SerialNum, SerialBindingReport
from bigfish.utils.encrypt import generate_serial_num, convert_to_base_x
from bigfish.utils.functions import format_admin_list


def batch_create_serial(modeladmin, request, queryset):
    queryset_list = []
    for i in range(0, 10):
        serial_num = generate_serial_num()
        encrypted_serial = convert_to_base_x(serial_num, 32)
        queryset_list.append(
            SerialNum(serial_num=serial_num, encrypted_serial=encrypted_serial, level_id=1, max_times=3))
    SerialNum.objects.bulk_create(queryset_list)


batch_create_serial.short_description = "批量创建序列号"


@admin.register(SerialLevel)
class SerialLevelAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SerialLevel)


@admin.register(SerialNum)
class SerialNumAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SerialNum)
    readonly_fields = ('serial_num', 'encrypted_serial')
    actions = [batch_create_serial]

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
        else:
            obj.serial_num = generate_serial_num()
            obj.encrypted_serial = convert_to_base_x(obj.serial_num, 32)
            super().save_model(request, obj, form, change)


@admin.register(SerialBindingRelation)
class SerialBindingRelationAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SerialBindingRelation)


@admin.register(SerialBindingReport)
class SerialBindingReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SerialBindingReport)
