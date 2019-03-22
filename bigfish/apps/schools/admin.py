from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from bigfish.apps.schools.models import Term, TermWeek, School, SchoolTerm, SchoolWeek, Klass, KlassProgress, \
    KlassActProgress, RegisterSerial
from bigfish.apps.users.models import UserKlassRelationship
from bigfish.utils.functions import format_admin_list
from bigfish.utils.register import RegisterSN


#
# @admin.register(Subjects)
# class SubjectsAdmin(admin.ModelAdmin):
#     list_display = format_admin_list(Subjects)
#     date_hierarchy = 'create_time'
#     show_full_result_count = False
#
#
# @admin.register(Segment)
# class SegmentAdmin(admin.ModelAdmin):
#     list_display = format_admin_list(Segment)
#     date_hierarchy = 'create_time'
#     show_full_result_count = False
#
#
# @admin.register(Grade)
# class GradeAdmin(admin.ModelAdmin):
#     list_display = format_admin_list(Grade)
#     date_hierarchy = 'create_time'
#     show_full_result_count = False
#
#
# @admin.register(SegmentGradeRel)
# class SegmentGradeRelAdmin(admin.ModelAdmin):
#     list_display = format_admin_list(SegmentGradeRel)
#     date_hierarchy = 'create_time'
#     show_full_result_count = False
#
#
# @admin.register(SchoolSegmentGradeRel)
# class SchoolSegmentGradeRelAdmin(admin.ModelAdmin):
#     list_display = format_admin_list(SchoolSegmentGradeRel)
#     date_hierarchy = 'create_time'
#     show_full_result_count = False


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Term)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'academic_year', 'term', 'description')
    list_filter = ('academic_year', 'term', 'is_active',)
    show_full_result_count = False


@admin.register(TermWeek)
class TermWeekAdmin(admin.ModelAdmin):
    list_display = format_admin_list(TermWeek)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'term__title', 'description')
    list_filter = ('is_active',)
    show_full_result_count = False


class SchoolResource(resources.ModelResource):
    class Meta:
        model = School


@admin.register(School)
class SchoolAdmin(ImportExportModelAdmin):
    resource_class = SchoolResource
    list_display = format_admin_list(School)
    date_hierarchy = 'create_time'
    raw_id_fields = ('areas',)
    search_fields = ('id', 'title', 'coding', 'en_title', 'subtitle', 'short_name', 'areas__name', 'description')
    list_filter = ('is_normal', 'use_cast', 'is_active', 'auto_remember_pwd')
    show_full_result_count = False


@admin.register(SchoolTerm)
class SchoolTermAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SchoolTerm)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'term__title', 'description', 'school__title')
    list_filter = ('term', 'is_active',)
    show_full_result_count = False


@admin.register(SchoolWeek)
class SchoolWeekAdmin(admin.ModelAdmin):
    list_display = format_admin_list(SchoolWeek)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'term_week__title', 'description', 'school__title')
    list_filter = ('is_active',)
    show_full_result_count = False


class KlassProgressInlines(admin.TabularInline):
    model = KlassProgress
    extra = 1
    verbose_name_plural = '班级进度'


class UserKlassInlines(admin.TabularInline):
    model = UserKlassRelationship
    raw_id_fields = ('user',)
    fields = ('user',)
    extra = 1
    verbose_name_plural = '用户班级关系列表'


@admin.register(Klass)
class KlassAdmin(admin.ModelAdmin):
    list_display = format_admin_list(Klass)
    inlines = (KlassProgressInlines, UserKlassInlines)
    date_hierarchy = 'create_time'
    search_fields = ('id', 'title', 'school__title', 'grade', 'publish__title', 'description')
    list_filter = ('is_active',)
    show_full_result_count = False

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        if request.user.identity in [4, 5] or request.user.is_superuser:
            qs = self.model._default_manager.get_queryset()
        else:
            klass_list = UserKlassRelationship.objects.filter(user=request.user, is_effect=True
                                                              ).values_list('klass_id', flat=True)
            qs = self.model._default_manager.get_queryset().filter(id__in=klass_list)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(KlassProgress)
class KlassProgressAdmin(admin.ModelAdmin):
    list_display = format_admin_list(KlassProgress)


@admin.register(KlassActProgress)
class KlassActProgressAdmin(admin.ModelAdmin):
    list_display = format_admin_list(KlassActProgress)


def batch_create_serial(modeladmin, request, queryset):
    queryset_list = []
    try:
        school = queryset.first().school
    except Exception as e:
        school = None
        coding = None
    else:
        coding = school.coding
    rs = RegisterSN()
    serial_num_list = rs.get_bulk_sn(coding)
    for serial_num in serial_num_list:
        encrypt_sn = rs.convert_to_base_x(serial_num, 64)
        queryset_list.append(RegisterSerial(serial_num=serial_num, encrypt_sn=encrypt_sn, school=school))
    RegisterSerial.objects.bulk_create(queryset_list)


batch_create_serial.short_description = "批量创建序列号"


@admin.register(RegisterSerial)
class RegisterSerialAdmin(admin.ModelAdmin):
    list_display = format_admin_list(RegisterSerial)
    readonly_fields = ('serial_num', 'encrypt_sn')
    actions = [batch_create_serial]

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
        else:
            rs = RegisterSN()
            school = form.cleaned_data.get('school', None)
            if school:
                coding = school.coding
            else:
                coding = None
            obj.serial_num = rs.get_serial_num(coding)
            obj.encrypt_sn = rs.convert_to_base_x(obj.serial_num, 64)
            super().save_model(request, obj, form, change)
