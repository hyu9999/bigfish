import xadmin
from xadmin.views import BaseAdminView, CommAdminView

from bigfish.utils.functions import format_admin_list, format_admin_search_fields, format_admin_editable


class BaseSetting(object):
    # 是否可更换主题
    enable_themes = True
    # 使用bootstrap样式
    use_bootswatch = True


xadmin.site.register(BaseAdminView, BaseSetting)


class GlobalSetting(object):
    # 标题
    site_title = "Big Fish 后台管理系统"
    # 页脚
    site_footer = "http://www.bigfish.com.cn/"
    # 菜单收缩
    menu_style = "accordion"


xadmin.site.register(CommAdminView, GlobalSetting)


def generate_xadmin_params(obj):
    list_display = format_admin_list(obj)
    list_filter = format_admin_list(obj)
    search_fields = format_admin_search_fields(obj)
    show_detail_fields = ('id',)
    list_editable = format_admin_editable(obj)
    ret_dict = {"list_display": list_display, "list_filter": list_filter, "search_fields": search_fields,
                "show_detail_fields": show_detail_fields, "list_editable": list_editable}
    return ret_dict
