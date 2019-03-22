from bigfish.utils.functions import format_admin_list
from django.contrib import admin

from bigfish.apps.areas.models import Area, ProvinceInfo


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Area)
    search_fields = ("coding", "name", "level", "prov_code", "city_code", "idealZoom")
    date_hierarchy = "update_time"
    list_filter = ("level", "is_active")


@admin.register(ProvinceInfo)
class ProvinceInfoAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ProvinceInfo)
