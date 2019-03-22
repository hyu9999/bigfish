from django.contrib import admin

# Register your models here.
from bigfish.apps.versus.models import Versus, VersusDetail


class VersusInlines(admin.TabularInline):
    model = VersusDetail
    extra = 1
    verbose_name_plural = '答题列表'


@admin.register(Versus)
class VersusAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'pk_user', 'competitor_type', 'complete_type', 'pk_type', 'classroom', 'start_time', 'end_time', 'competitor',
        'user_ai')
    list_filter = ('competitor_type', 'complete_type', 'pk_type', 'pk_user',)
    search_fields = ('pk_user__username',)
    list_editable = ('competitor',)
    inlines = (VersusInlines,)
    fieldsets = (
        (
            '基本信息',
            {'fields': (('pk_type', 'complete_type', 'classroom'), ('start_time', 'end_time'),), }
        ),
        (
            '用户对战信息',
            {'fields': (
                ('pk_user', 'pk_result'), 'pet_name', 'speed', ('score', 'real_score', 'big_fishery'),
                ('right_times', 'wrong_times', 'total_times')), }
        ),
        (
            '对手信息',
            {'fields': ('competitor_type', 'competitor',), }
        ),
        (
            'AI对手信息',
            {'fields': (
                ('user_ai', 'pk_result_ai'), 'pet_name_ai', 'speed_ai',
                ('score_ai', 'real_score_ai', 'big_fishery_ai',),
                ('right_times_ai', 'wrong_times_ai', 'total_times_ai'),), }
        ),

    )


@admin.register(VersusDetail)
class VersusDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'versus', 'order', 'user_type', 'word', 'question_type', 'result')
    list_filter = ('user_type', 'question_type')
    search_fields = ('word__spell',)
