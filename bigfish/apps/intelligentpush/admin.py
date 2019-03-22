from django.contrib import admin

# Register your models here.
from bigfish.apps.intelligentpush.models import IntelligentPush, PushQuestions
from bigfish.utils.functions import format_admin_list


@admin.register(IntelligentPush)
class IntelligentPushAdmin(admin.ModelAdmin):
    list_display = format_admin_list(IntelligentPush)
    date_hierarchy = 'update_time'
    fieldsets = (
        ("推送信息", {'fields': [('push_user',), 'is_homework', 'push_type']}),
        ("年级信息", {'fields': [('areas_code', 'areas_name'), ('school_id', 'school_name'),
                             'grade_name', ('klass_id', 'klass_name'), ]}),
        ("教材信息", {'fields': [('publish_id', 'publish_name', 'term_num'),
                             ('unit_id', 'unit_name'), ('lesson_id', 'lesson_name')]}),
        ("个人信息", {'fields': [('user_id', 'username', 'realname', 'nickname'), ]}),
        ("活动信息", {'fields': [('task_id', 'task_name'), ('activity_id', 'activity_name'), ]}),
    )


@admin.register(PushQuestions)
class PushQuestionsAdmin(admin.ModelAdmin):
    list_display = format_admin_list(PushQuestions)
    date_hierarchy = 'update_time'
    raw_id_fields = ('intelligent_push',)
    fieldsets = (
        ("推送信息", {'fields': ['intelligent_push', 'push_user', 'is_homework', 'push_type']}),
        ("题目信息", {'fields': ['question_id', 'question_content', ]}),
        ("年级信息", {'fields': [('areas_code', 'areas_name'), ('school_id', 'school_name'),
                             'grade_name', ('klass_id', 'klass_name'), ]}),
        ("教材信息", {'fields': [('publish_id', 'publish_name', 'term_num'),
                             ('unit_id', 'unit_name'), ('lesson_id', 'lesson_name')]}),
        ("个人信息", {'fields': [('user_id', 'username', 'realname', 'nickname'), ]}),
        ("活动信息", {'fields': [('task_id', 'task_name'), ('activity_id', 'activity_name'), ]}),
    )
