import xadmin

from bigfish.apps.bigfish.adminx import generate_xadmin_params
from bigfish.apps.reports.models import EnterStudy, Conversation, ReviewData, SaveDataInfo, SaveDataDetails, \
    StudentDailyData, KlassDailyData, SchoolDailyData, ActivityDailyData
from bigfish.utils.functions import format_admin_list, format_admin_search_fields


class EnterStudyXAdmin(object):
    params = generate_xadmin_params(EnterStudy)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(EnterStudy, EnterStudyXAdmin)


class ConversationXAdmin(object):
    obj = Conversation
    list_display = (
        'id', 'owner', 'bot_time', 'user_voice_query', 'user_time', 'question_id', 'question_type', 'input',
        'input_type', 'error_count', 'enterstudy_id')
    list_filter = ('owner', 'input', 'input_type')
    search_fields = ('owner', 'input', 'input_type')
    list_per_page = 10


xadmin.site.register(Conversation, ConversationXAdmin)


class SaveDataInfoXAdmin(object):
    list_display = ('user', 'task', 'unit', 'lesson', 'activity', 'answer_right_times')
    list_filter = ('user',)
    search_fields = ('user',)
    list_per_page = 10


xadmin.site.register(SaveDataInfo, SaveDataInfoXAdmin)


class SaveDataDetailsXAdmin(object):
    list_display = ('save_data', 'question_id', 'is_right', 'question_type', 'voice_url', 'answer_detail')
    list_per_page = 10


xadmin.site.register(SaveDataDetails, SaveDataDetailsXAdmin)


class SchoolDailyDataXAdmin(object):
    params = generate_xadmin_params(SchoolDailyData)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(SchoolDailyData, SchoolDailyDataXAdmin)


class KlassDailyDataXAdmin(object):
    params = generate_xadmin_params(KlassDailyData)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(KlassDailyData, KlassDailyDataXAdmin)


class StudentDailyDataXAdmin(object):
    params = generate_xadmin_params(StudentDailyData)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(StudentDailyData, StudentDailyDataXAdmin)


class ActivityDailyDataXAdmin(object):
    params = generate_xadmin_params(ActivityDailyData)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(ActivityDailyData, ActivityDailyDataXAdmin)
