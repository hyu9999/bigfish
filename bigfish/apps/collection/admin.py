from django.contrib import admin

from bigfish.apps.collection.models import UserVoice, UserPhoto
from bigfish.utils.functions import format_admin_list


@admin.register(UserVoice)
class UserVoiceAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserVoice)


@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserPhoto)
