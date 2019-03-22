from django.contrib import admin

# Register your models here.
from bigfish.apps.overall.models import KlassData, SchoolData, DistrictData, CityData, ProvinceData
from bigfish.utils.functions import format_admin_list, format_admin_search_fields


@admin.register(KlassData)
class KlassDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(KlassData)
    search_fields = format_admin_search_fields(KlassData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']


@admin.register(SchoolData)
class SchoolDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(SchoolData)
    search_fields = format_admin_search_fields(SchoolData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']


@admin.register(DistrictData)
class DistrictDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(DistrictData)
    search_fields = format_admin_search_fields(DistrictData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']


@admin.register(CityData)
class CityDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(CityData)
    search_fields = format_admin_search_fields(CityData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']


@admin.register(ProvinceData)
class ProvinceDataAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = format_admin_list(ProvinceData)
    search_fields = format_admin_search_fields(ProvinceData)
    date_hierarchy = 'create_time'
    list_filter = ['term_id']
