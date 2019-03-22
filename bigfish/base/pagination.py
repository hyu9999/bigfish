# coding: utf-8
"""
Pagination serializers determine the structure of the output that should
be used for paginated responses.
"""
from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def fmt_ret_msg_200(msg={}, extra=None):
    base_dict = OrderedDict([
        ('message', "success"),
        ('code', 200),
        ('data', msg),
    ])
    if isinstance(extra, dict):
        base_dict.update(extra)
    return base_dict


class BFPageNumberPagination(PageNumberPagination):
    """
    分页类

    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        ret_data = OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])
        return Response(fmt_ret_msg_200(ret_data))
