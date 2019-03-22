from django.contrib import admin

from bigfish.apps.wrongtopic.models import WrongTopic, WrongTopicHis
from bigfish.utils.functions import format_admin_list


@admin.register(WrongTopic)
class WrongTopicAdmin(admin.ModelAdmin):
    list_display = format_admin_list(WrongTopic)
    date_hierarchy = 'update_time'
    fieldsets = (
        ("知识点信息", {'fields': [('kp_coding', 'kp_name',), ]}),
        ("错题本信息", {'fields': ['master_level', 'scene', ]}),
        ("年级信息", {'fields': [('areas_code', 'areas_name'), ('school_id', 'school_name'),
                             'grade_name', ('klass_id', 'klass_name'), ]}),
        ("教材信息", {'fields': [('publish_id', 'publish_name', 'term_num'),
                             ('unit_id', 'unit_name'), ('lesson_id', 'lesson_name')]}),
        ("个人信息", {'fields': [('user_id', 'username', 'realname', 'nickname'), ]}),
        ("活动信息", {'fields': [('task_id', 'task_name'), ('activity_id', 'activity_name'), ]}),
    )


@admin.register(WrongTopicHis)
class WrongTopicHisAdmin(admin.ModelAdmin):
    list_display = format_admin_list(WrongTopicHis)
    date_hierarchy = 'update_time'
    raw_id_fields = ('wrong_topic',)
    fieldsets = (
        ("知识点信息", {'fields': [('kp_coding', 'kp_name',), ]}),
        ("错题本信息", {'fields': ['wrong_topic', 'master_level', 'scene', ]}),
        ("年级信息", {'fields': [('areas_code', 'areas_name'), ('school_id', 'school_name'),
                             'grade_name', ('klass_id', 'klass_name'), ]}),
        ("教材信息", {'fields': [('publish_id', 'publish_name', 'term_num'),
                             ('unit_id', 'unit_name'), ('lesson_id', 'lesson_name')]}),
        ("个人信息", {'fields': [('user_id', 'username', 'realname', 'nickname'), ]}),
        ("活动信息", {'fields': [('task_id', 'task_name'), ('activity_id', 'activity_name'), ]}),
        ("其他", {'fields': ['update_time', 'add_time']})
    )
