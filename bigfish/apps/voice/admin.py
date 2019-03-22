from django.contrib import admin

from bigfish.apps.voice.models import SpeechEvaluation, SpeechEvaluationReport, SpeechEvaluationDetail
from bigfish.utils.functions import format_admin_list


@admin.register(SpeechEvaluation)
class SpeechEvaluationAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SpeechEvaluation)


@admin.register(SpeechEvaluationDetail)
class SpeechEvaluationDetailAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SpeechEvaluationDetail)


@admin.register(SpeechEvaluationReport)
class SpeechEvaluationReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SpeechEvaluationReport, remove=['result', 'voice_recognition'])
    date_hierarchy = 'create_time'
    search_fields = ('id', 'name')
    raw_id_fields = ('classroom', 'activity_report', 'activity', 'user', 'eval_type')
    show_full_result_count = False
