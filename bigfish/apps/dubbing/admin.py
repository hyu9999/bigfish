from django.contrib import admin

from bigfish.apps.dubbing.models import DubbingSRC, UserDubbing, DubbingZan, DubbingRead, \
    DubbingCategory, DubbingMain, DubbingClick, Competition, SubCompetition, CompetitionRank, CompetitionImg, \
    CompetitionImgRelationship, AreaCompetition, RewardConfig
from bigfish.utils.functions import format_admin_list


@admin.register(DubbingMain)
class DubbingMainAdmin(admin.ModelAdmin):
    list_display = format_admin_list(DubbingMain)


@admin.register(DubbingCategory)
class DubbingCategoryAdmin(admin.ModelAdmin):
    list_display = format_admin_list(DubbingCategory)


@admin.register(DubbingSRC)
class DubbingSRCAdmin(admin.ModelAdmin):
    list_display = format_admin_list(DubbingSRC, remove=['dialogue', 'score_rule', 'create_time'])
    search_fields = ('is_lesson', 'is_active', 'grouping',)
    list_filter = ('is_lesson', 'is_active', 'grouping',)


@admin.register(UserDubbing)
class UserDubbingAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserDubbing)
    search_fields = ('user__username',)
    date_hierarchy = 'create_time'


@admin.register(DubbingClick)
class DubbingClickAdmin(admin.ModelAdmin):
    list_display = format_admin_list(DubbingClick)


@admin.register(DubbingZan)
class DubbingZanAdmin(admin.ModelAdmin):
    list_display = format_admin_list(DubbingZan)


@admin.register(DubbingRead)
class DubbingReadAdmin(admin.ModelAdmin):
    list_display = format_admin_list(DubbingRead)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Competition)


@admin.register(AreaCompetition)
class AreaCompetitionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(AreaCompetition)


@admin.register(SubCompetition)
class SubCompetitionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SubCompetition)


@admin.register(CompetitionRank)
class CompetitionRankAdmin(admin.ModelAdmin):
    list_display = format_admin_list(CompetitionRank)


@admin.register(CompetitionImg)
class CompetitionImgAdmin(admin.ModelAdmin):
    list_display = format_admin_list(CompetitionImg)


@admin.register(CompetitionImgRelationship)
class CompetitionImgRelationshipAdmin(admin.ModelAdmin):
    list_display = format_admin_list(CompetitionImgRelationship)


@admin.register(RewardConfig)
class RewardConfigAdmin(admin.ModelAdmin):
    list_display = format_admin_list(RewardConfig)
