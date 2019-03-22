from django.contrib import admin

from bigfish.apps.achievement.models import Achievement, UserAchievement
from bigfish.utils.functions import format_admin_list


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Achievement)
    search_fields = ('id', 'title', 'en_title', 'content', 'en_content', 'description')
    list_filter = ('is_active',)
    show_full_result_count = False


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner', 'achievement', 'status', 'progress')
    search_fields = ('owner__username',)
    list_filter = ('owner', 'achievement', 'status', 'progress')
