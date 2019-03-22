import datetime
import os

from django.contrib import admin

from django.conf import settings
from bigfish.utils.functions import format_admin_list
from bigfish.apps.versionupdate.models import Version, UpdatePublish, UpdateConfig, UpdateDetail, UpdateException,\
    SourceDetail, IdentityVersion

from bigfish.utils.resource_package import zip_dir


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Version)
    list_filter = ('version_name',)
    search_fields = ('version_name',)

    def save_model(self, request, obj, form, change):
        version_name = request.POST.get('version_name')
        version_dir = os.path.join(settings.MEDIA_ROOT, 'version', version_name)
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
        # 保存文件夹路径
        # obj.folder_name = version_dir
        super().save_model(request, obj, form, change)


@admin.register(UpdatePublish)
class UpdatePublishAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UpdatePublish)
    list_filter = ('publish',)
    search_fields = ('publish',)


@admin.register(UpdateConfig)
class UpdateConfigAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UpdateConfig)
    list_filter = ('area',)
    search_fields = ('area',)


@admin.register(UpdateDetail)
class UpdateDetailAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UpdateDetail)

    def save_model(self, request, obj, form, change):
        # if change:
        #     pass
        # else:
        folder_name = request.POST.get('folder_name')
        zip_name = request.POST.get('zip_name', None)
        if zip_name is None:
            zip_name = zip_name
        else:
            zip_name = '{}-{}.zip'.format(datetime.datetime.now().strftime('%Y-%m-%d'), folder_name.split('/')[-1])
        # 版本号文件夹
        version_name = obj.update_publish.identity.version.version_name
        version_dir = os.path.join(settings.MEDIA_ROOT, 'version', version_name)
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
        zip_dir(folder_name, os.path.join(version_dir, '{}'.format(zip_name)))
        obj.zip_name = zip_name
        super().save_model(request, obj, form, change)


@admin.register(UpdateException)
class UpdateExceptionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UpdateException)
    list_filter = ('username',)
    search_fields = ('username',)


@admin.register(SourceDetail)
class SourceDetailAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SourceDetail)
    list_filter = ('username',)
    search_fields = ('username',)


@admin.register(IdentityVersion)
class IdentityVersionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(IdentityVersion)
    list_filter = ('apk_name',)
    search_fields = ('apk_name',)