from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from bigfish.apps.textbooks.models import PublishVersion, Textbook, Unit, Lesson, ActTab, ActType, \
    Activity, PrepareAdvise
from bigfish.base.admin import BaseAdmin
from bigfish.utils.functions import format_admin_list


class TextbookInlines(admin.TabularInline):
    model = Textbook
    extra = 1
    verbose_name_plural = '教材册目'


class UnitInlines(admin.TabularInline):
    model = Unit
    extra = 1
    verbose_name_plural = '单元'


class LessonInlines(admin.TabularInline):
    model = Lesson
    extra = 1
    verbose_name_plural = '课程'


class ActivityInlines(admin.TabularInline):
    model = Activity
    extra = 1
    verbose_name_plural = '活动'


@admin.register(PublishVersion)
class PublishVersionAdmin(BaseAdmin):
    list_display = format_admin_list(PublishVersion, remove=['subtitle', 'en_subtitle'])
    raw_id_fields = ('image',)
    search_fields = ('id', 'title', 'en_title', 'short_name', 'order', 'description')
    inlines = (TextbookInlines,)


@admin.register(Textbook)
class TextbookAdmin(BaseAdmin):
    list_display = format_admin_list(Textbook, remove=['subtitle', 'en_subtitle'])
    raw_id_fields = ('image', 'publish')
    search_fields = ('id', 'title', 'en_title', 'short_name', 'order', 'description')
    list_filter = ('publish', 'grade', 'term', 'is_active',)
    inlines = (UnitInlines,)


@admin.register(Unit)
class UnitAdmin(BaseAdmin):
    list_display = format_admin_list(Unit)
    raw_id_fields = ('image', 'textbook', 'video')
    search_fields = ('id', 'title', 'en_title', 'subtitle', 'en_subtitle', 'short_name', 'order', 'description')
    list_filter = ('textbook', 'is_active',)
    inlines = (LessonInlines,)


@admin.register(Lesson)
class LessonAdmin(BaseAdmin):
    list_display = format_admin_list(Lesson)
    raw_id_fields = ('image', 'unit')
    search_fields = ('id', 'title', 'en_title', 'subtitle', 'en_subtitle', 'short_name', 'order', 'description')
    list_filter = ('unit', 'is_active',)
    inlines = (ActivityInlines,)
    list_per_page = 10


@admin.register(ActTab)
class ActTabAdmin(BaseAdmin):
    list_display = format_admin_list(ActTab, remove=['subtitle', 'en_subtitle', 'short_name', ])
    raw_id_fields = ('pc_image', 'app_image')
    search_fields = ('id', 'title', 'en_title', 'order', 'description')
    list_per_page = 10


@admin.register(Activity)
class ActivityAdmin(BaseAdmin):
    list_display = format_admin_list(Activity,
                                     remove=['subtitle', 'en_subtitle', 'short_name', 'prepare_advise', 'rule_data'])
    raw_id_fields = ('publish', 'textbook', 'unit', 'lesson', 'act_tab', 'act_type', 'image', 'prepare_advise')
    search_fields = ('id', 'title', 'en_title', 'unit__title', 'lesson__title', 'act_type__third_type',
                     'description')
    list_filter = ('publish', 'textbook', 'act_tab', 'display_type', 'is_active')
    list_per_page = 10


@admin.register(ActType)
class ActTypeAdmin(ImportExportModelAdmin):
    list_display = format_admin_list(ActType)
    search_fields = ('id', 'first_type', 'second_type', 'third_type')
    list_filter = ('first_type', 'second_type',)
    list_per_page = 10


@admin.register(PrepareAdvise)
class PrepareAdviseAdmin(ImportExportModelAdmin):
    list_display = format_admin_list(PrepareAdvise)
