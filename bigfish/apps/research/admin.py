from django.contrib import admin

from bigfish.apps.research.models import PrepareLesson, PrepareLessonReply, PrepareLessonWatch, TeachingLog, \
    TeachingLogReply, TeachingLogWatch, ResearchActivity, ResearchActivityReply, ResearchActivityWatch, TeacherSchedule, \
    TeachingEffect
from bigfish.utils.functions import format_admin_list


@admin.register(PrepareLesson)
class PrepareLessonAdmin(admin.ModelAdmin):
    list_display = format_admin_list(PrepareLesson)


@admin.register(PrepareLessonReply)
class PrepareLessonReplyAdmin(admin.ModelAdmin):
    list_display = format_admin_list(PrepareLessonReply)


@admin.register(PrepareLessonWatch)
class PrepareLessonWatchAdmin(admin.ModelAdmin):
    list_display = format_admin_list(PrepareLessonWatch)


@admin.register(TeachingLog)
class TeachingLogAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TeachingLog)


@admin.register(TeachingLogReply)
class TeachingLogReplyAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TeachingLogReply)


@admin.register(TeachingLogWatch)
class TeachingLogWatchAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TeachingLogWatch)


@admin.register(ResearchActivity)
class ResearchActivityAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ResearchActivity)


@admin.register(ResearchActivityReply)
class ResearchActivityAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ResearchActivityReply)


@admin.register(ResearchActivityWatch)
class ResearchActivityWatchAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ResearchActivityWatch)


@admin.register(TeacherSchedule)
class TeacherScheduleAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TeacherSchedule)
    list_filter = ('teacher', 'klass',)


@admin.register(TeachingEffect)
class TeachingEffectAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TeachingEffect)
    date_hierarchy = 'update_time'
