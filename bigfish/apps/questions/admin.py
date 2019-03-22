from django.contrib import admin

from bigfish.apps.questions.models import Question, QuestionKPRelationship
from bigfish.utils.functions import format_admin_list


class QuestionKPRelationshipInline(admin.TabularInline):
    model = Question.knowledge_point.through
    extra = 0
    verbose_name_plural = '题目-知识点关系'


@admin.register(QuestionKPRelationship)
class QuestionKPRelationshipAdmin(admin.ModelAdmin):
    list_display = format_admin_list(QuestionKPRelationship)
    date_hierarchy = 'update_time'
    raw_id_fields = ('question', 'knowledge_point')
    save_as = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('show_type',)
    # list_display = generate_fields(Question, add=['id'])
    list_display = ('id', 'version', 'grade', 'volume', 'unit', 'lesson', 'question_type', 'show_type',
                    'difficulty', 'name', 'desc', 'content', 'option_type', 'options', 'answer', 'suitable',
                    'purpose', 'label')
    fieldsets = (
        ("年级信息", {'fields': [('grade', 'volume', 'version',), ]}),
        ("教材信息", {'fields': [('textbook', 'unit', 'lesson'), ]}),
        ("题目信息", {
            'fields': [('name', 'question_type', 'show_type'), 'content', ('options', 'option_type'),
                       ('answer', 'difficulty'), 'desc', 'suitable', 'purpose', 'label']}),
        ("其他", {'fields': [('is_push',), ]}),
    )
    inlines = (QuestionKPRelationshipInline,)
    raw_id_fields = ('knowledge_point',)
    search_fields = ('id', 'name')
