import xadmin

from bigfish.apps.bigfish.adminx import generate_xadmin_params
from bigfish.apps.shop.models import Wordhero, Userhero


class WordheroXAdmin(object):
    params = generate_xadmin_params(Wordhero)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(Wordhero, WordheroXAdmin)


class UserheroXAdmin(object):
    params = generate_xadmin_params(Userhero)
    list_display = params['list_display']
    list_filter = params['list_filter']
    search_fields = params['search_fields']
    show_detail_fields = params['show_detail_fields']
    list_editable = params['list_editable']


xadmin.site.register(Userhero, UserheroXAdmin)
