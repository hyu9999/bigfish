from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from bigfish.apps.users.models import BigfishUser, UserOnline, UserKlassRelationship, UserChangeReport, \
    UserFeedback, UserUsedInfo, UserWordHero, UserCourse, UserReg, UserPosition, UserScenariosReport
from bigfish.utils.functions import format_admin_list


class KlassInlines(admin.TabularInline):
    model = UserKlassRelationship
    extra = 1
    verbose_name_plural = '班级列表'


class UserRegInlines(admin.TabularInline):
    model = UserReg


class UserCourseInlines(admin.TabularInline):
    model = UserCourse


@admin.register(BigfishUser)
class BigfishUserAdmin(UserAdmin):
    list_display = format_admin_list(BigfishUser, remove=['password'])
    raw_id_fields = ('area', 'school')
    date_hierarchy = 'modified'
    filter_horizontal = ('attend_class', 'user_permissions', 'groups', 'control_area')
    inlines = (UserCourseInlines, UserRegInlines, KlassInlines)
    search_fields = ('username', 'realname', 'card_id', 'student_code', 'province_code', 'school__title')
    ordering = ('username',)
    list_filter = ('is_active', 'is_formal', 'identity', 'is_staff', 'is_superuser')
    fieldsets = [
        (None, {'fields': ('username', 'password',)}),
        ("基本信息", {'fields': [('realname', 'nickname',),
                             ('first_name', 'last_name',),
                             'identity', 'area', 'icon', 'sex', 'email', 'telephone', 'card_id',
                             ]}),
        ("权限信息", {'fields': ['school', 'user_permissions', 'groups', 'control_area', 'is_superuser', 'is_staff',
                             'is_active', 'is_formal']}),
        ("登录信息", {'fields': [('first_login', 'date_joined',)]}),
        ("朋友圈信息", {'fields': [('attention_num', 'fans_num',)]}),
        ("班级信息", {'fields': [('student_code', 'province_code')]}),

    ]

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        if request.user.identity in [4, 5] or request.user.is_superuser:
            qs = self.model._default_manager.get_queryset()
        else:
            qs = self.model._default_manager.get_queryset().filter(id=request.user.id)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        if request.user.is_superuser or request.user.identity in [4, 5]:
            self.readonly_fields = ()
        else:
            if request.user == obj:
                self.readonly_fields = (
                    'username', 'identity', 'groups', 'user_permissions', 'is_superuser', 'control_area',
                    'is_staff', 'is_active', 'first_login', 'date_joined', 'attention_num', 'fans_num', 'student_code',
                    'province_code')
            else:
                self.readonly_fields = (
                    'username', 'realname', 'nickname', 'password', 'first_name', 'last_name', 'identity', 'area',
                    'icon', 'sex', 'email', 'telephone', 'user_permissions', 'groups', 'control_area', 'is_superuser',
                    'is_staff', 'is_active', 'first_login', 'date_joined', 'attention_num', 'fans_num', 'card_id',
                    'student_code', 'province_code')

        return self.readonly_fields

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if request.user.is_superuser or request.user.identity in [4, 5]:
            for inline_class in self.inlines:
                inline = inline_class(self.model, self.admin_site)
                if request:
                    if not (inline.has_add_permission(request) or
                            inline.has_change_permission(request, obj) or
                            inline.has_delete_permission(request, obj)):
                        continue
                    if not inline.has_add_permission(request):
                        inline.max_num = 0
                inline_instances.append(inline)

        return inline_instances


@admin.register(UserKlassRelationship)
class UserKlassRelationshipAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserKlassRelationship)

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        if request.user.is_superuser:
            qs = self.model._default_manager.get_queryset()
        else:
            qs = self.model._default_manager.get_queryset().filter(user=request.user)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(UserOnline)
class UserOnlineAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserOnline)


@admin.register(UserChangeReport)
class UserChangeReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserChangeReport)


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserFeedback)


@admin.register(UserUsedInfo)
class UserUsedInfoAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserUsedInfo)


@admin.register(UserWordHero)
class UserWordHeroAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserWordHero)


@admin.register(UserPosition)
class UserPositionAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserPosition)


@admin.register(UserScenariosReport)
class UserScenariosReportAdmin(admin.ModelAdmin):
    list_display = format_admin_list(UserScenariosReport)
