from import_export.admin import ImportExportModelAdmin


class BaseAdmin(ImportExportModelAdmin):
    date_hierarchy = 'create_time'
    list_filter = ('is_active',)
    show_full_result_count = False

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
