from bigfish.utils.functions import format_admin_list
from django.contrib import admin

from bigfish.apps.public.models import Public, AppTable, ATGroup


@admin.register(Public)
class PublicAdmin(admin.ModelAdmin):
    list_filter = ('title',)
    list_display = format_admin_list(Public)
    search_fields = ('title', 'content')


@admin.register(ATGroup)
class ATGroupAdmin(admin.ModelAdmin):
    list_filter = ('title',)
    list_display = format_admin_list(ATGroup)
    search_fields = ('title',)


@admin.register(AppTable)
class AppTableAdmin(admin.ModelAdmin):
    list_filter = ('title',)
    list_display = format_admin_list(AppTable)
    search_fields = ('title',)
