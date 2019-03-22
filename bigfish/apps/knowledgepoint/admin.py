from django.contrib import admin

from bigfish.apps.knowledgepoint.models import KnowledgePoint
from bigfish.utils.functions import format_admin_list


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = format_admin_list(KnowledgePoint)
    date_hierarchy = 'update_time'
    search_fields = ('coding', 'title', 'en_title', 'order', 'parent_code', 'desc')
    list_filter = ('root', 'level', 'has_children', 'curriculum_standard', 'part_of_speech',)
    show_full_result_count = False
