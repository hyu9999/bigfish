from django.contrib import admin

from bigfish.apps.attention.models import AttentionCircle
from bigfish.utils.functions import format_admin_list


@admin.register(AttentionCircle)
class AttentionCircleAdmin(admin.ModelAdmin):
    list_display = format_admin_list(AttentionCircle)
    raw_id_fields = ('user', 'fans')
    search_fields = ('user__username', 'fans__username')
    list_filter = ('each_other',)
