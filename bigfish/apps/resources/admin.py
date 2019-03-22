from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from bigfish.apps.resources.models import Video, Audio, Image, \
    ImageType, Amazon, Pet, LocResInfo
from bigfish.utils.functions import format_admin_list


class BaseModel(ImportExportActionModelAdmin):
    date_hierarchy = 'create_time'
    list_filter = ('is_active',)
    show_full_result_count = False
    list_per_page = 20
@admin.register(Video)
class VideoAdmin(BaseModel):
    list_display = format_admin_list(Video)
    search_fields = ('id', 'title', 'res', 'description')


@admin.register(Audio)
class AudioAdmin(BaseModel):
    list_display = format_admin_list(Audio)
    search_fields = ('id', 'title', 'res', 'description')


@admin.register(ImageType)
class ImageTypeAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ImageType)
    search_fields = ('id', 'title', 'order', 'description')


@admin.register(Image)
class ImageAdmin(BaseModel):
    list_display = format_admin_list(Image)
    search_fields = ('id', 'title', 'res', 'description')


@admin.register(Pet)
class PetAdmin(BaseModel):
    list_display = format_admin_list(Pet)
    search_fields = ('id', 'title', 'image__res', 'thumbnail__res', 'description')
    list_filter = ('is_active', 'is_free')


@admin.register(Amazon)
class AmazonAdmin(BaseModel):
    list_display = format_admin_list(Amazon)
    search_fields = ('id', 'title', 'text', 'tts_girl', 'tts_boy', 'description')


@admin.register(LocResInfo)
class LocResInfoAdmin(BaseModel):
    list_display = format_admin_list(LocResInfo)
    search_fields = ('id', 'title', 'loc_url', 'description')
