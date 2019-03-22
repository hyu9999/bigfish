from django.contrib import admin

from bigfish.apps.bfwechat.models import ActiveToken, MediaSource, KeyWord, SendMsg, TemplateMsg, \
    TemplateMsgRecord, WxUser, WxUserRelationship, Feedback, WxArticleMsg, WxArticleMsgRecord
from bigfish.utils.functions import format_admin_list


@admin.register(ActiveToken)
class ActiveTokenAdmin(admin.ModelAdmin):
    list_display = format_admin_list(ActiveToken)


@admin.register(MediaSource)
class MediaSourceAdmin(admin.ModelAdmin):
    list_display = format_admin_list(MediaSource)


@admin.register(KeyWord)
class KeyWordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(KeyWord)


@admin.register(SendMsg)
class SendMsgAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SendMsg)


@admin.register(TemplateMsg)
class TemplateMsgAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TemplateMsg)


@admin.register(TemplateMsgRecord)
class TemplateMsgRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TemplateMsgRecord)


@admin.register(WxArticleMsg)
class WxArticleMsgAdmin(admin.ModelAdmin):
    list_display = format_admin_list(WxArticleMsg)


@admin.register(WxArticleMsgRecord)
class WxArticleMsgRecordAdmin(admin.ModelAdmin):
    list_display = format_admin_list(WxArticleMsgRecord)


@admin.register(WxUser)
class WxUserAdmin(admin.ModelAdmin):
    list_display = format_admin_list(WxUser, remove=["student"])
    date_hierarchy = "add_time"


@admin.register(WxUserRelationship)
class WxUserRelationshipAdmin(admin.ModelAdmin):
    list_display = format_admin_list(WxUserRelationship)
    date_hierarchy = "add_time"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Feedback)
    date_hierarchy = "add_time"
