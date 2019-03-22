from import_export.admin import ImportExportModelAdmin

from bigfish.apps.contents.models import Article, Sentence, WordType, TextbookWord
from bigfish.utils.functions import format_admin_list
from django.contrib import admin


@admin.register(Article)
class ArticleAdmin(ImportExportModelAdmin):
    list_display = format_admin_list(Article)
    raw_id_fields = ('image', 'video', 'audio')
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'en_title', 'content', 'en_content', 'description')
    list_filter = ('is_active', 'classify')
    show_full_result_count = False


@admin.register(Sentence)
class SentenceAdmin(ImportExportModelAdmin):
    list_display = format_admin_list(Sentence)
    raw_id_fields = ('image', 'video', 'audio', 'knowledge_point', 'article', 'role')
    filter_horizontal = ('word_kp',)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'en_title', 'content', 'en_content', 'description')
    list_filter = ('is_active',)
    show_full_result_count = False


@admin.register(WordType)
class WordTypeAdmin(ImportExportModelAdmin):
    list_display = format_admin_list(WordType)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'description')
    list_filter = ('is_active',)
    show_full_result_count = False


@admin.register(TextbookWord)
class TextbookWordAdmin(ImportExportModelAdmin):
    list_display = format_admin_list(TextbookWord)
    raw_id_fields = ('image', 'video', 'audio', 'microtext', 'knowledge_point', 'lesson', 'word_type')
    filter_horizontal = ('animation',)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'en_title', 'content', 'en_content', 'description')
    list_filter = ('is_active',)
    show_full_result_count = False
