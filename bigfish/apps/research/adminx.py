import xadmin

from bigfish.apps.bigfish.adminx import generate_xadmin_params
from bigfish.apps.research.models import TermSchedule, TeacherSchedule, SchoolWeek, PrepareLesson, PrepareLessonReply, \
    PrepareLessonWatch, TeachingLog, TeachingLogReply, TeachingLogWatch, ResearchActivity, ResearchActivityReply, \
    ResearchActivityWatch


class TermScheduleXAdmin(object):
    params = generate_xadmin_params(TermSchedule)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(TermSchedule, TermScheduleXAdmin)


class TeacherScheduleXAdmin(object):
    params = generate_xadmin_params(TeacherSchedule)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(TeacherSchedule, TeacherScheduleXAdmin)


class SchoolWeekXAdmin(object):
    params = generate_xadmin_params(SchoolWeek)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(SchoolWeek, SchoolWeekXAdmin)


class PrepareLessonXAdmin(object):
    params = generate_xadmin_params(PrepareLesson)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(PrepareLesson, PrepareLessonXAdmin)


class PrepareLessonReplyXAdmin(object):
    params = generate_xadmin_params(PrepareLessonReply)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(PrepareLessonReply, PrepareLessonReplyXAdmin)


class PrepareLessonWatchXAdmin(object):
    params = generate_xadmin_params(PrepareLessonWatch)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(PrepareLessonWatch, PrepareLessonWatchXAdmin)


class TeachingLogXAdmin(object):
    params = generate_xadmin_params(TeachingLog)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(TeachingLog, TeachingLogXAdmin)


class TeachingLogReplyXAdmin(object):
    params = generate_xadmin_params(TeachingLogReply)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(TeachingLogReply, TeachingLogReplyXAdmin)


class TeachingLogWatchXAdmin(object):
    params = generate_xadmin_params(TeachingLogWatch)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(TeachingLogWatch, TeachingLogWatchXAdmin)


class ResearchActivityXAdmin(object):
    params = generate_xadmin_params(ResearchActivity)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(ResearchActivity, ResearchActivityXAdmin)


class ResearchActivityReplyXAdmin(object):
    params = generate_xadmin_params(ResearchActivityReply)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(ResearchActivityReply, ResearchActivityReplyXAdmin)


class ResearchActivityWatchXAdmin(object):
    params = generate_xadmin_params(ResearchActivityWatch)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(ResearchActivityWatch, ResearchActivityWatchXAdmin)
