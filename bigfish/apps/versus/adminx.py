import xadmin

from bigfish.apps.bigfish.adminx import generate_xadmin_params
from bigfish.apps.versus.models import Versus, VersusDetail
from bigfish.utils.functions import format_admin_list, format_admin_search_fields


class VersusXAdmin(object):
    list_display = format_admin_list(Versus)
    list_filter = format_admin_list(Versus)
    search_fields = format_admin_search_fields(Versus)


xadmin.site.register(Versus, VersusXAdmin)


class VersusDetailXAdmin(object):
    list_display = format_admin_list(VersusDetail)
    list_filter = format_admin_list(VersusDetail)
    search_fields = format_admin_list(VersusDetail)


xadmin.site.register(VersusDetail, VersusDetailXAdmin)
