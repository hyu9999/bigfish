from django.contrib import admin

from bigfish.apps.integral.models import IntegralReport, UserIntegral
from bigfish.utils.functions import format_admin_list


@admin.register(UserIntegral)
class UserIntegralAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserIntegral)


@admin.register(IntegralReport)
class IntegralReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(IntegralReport)
