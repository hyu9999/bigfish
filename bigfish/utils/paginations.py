# encoding: utf-8

"""
@author: h3l
@contact: xidianlz@gmail.com
@file: paginations.py
@time: 2017/7/15 16:55
"""
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from bigfish.base.response import BFValidationError


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 40


def common_paging(obj_list, request):
    """
    objs : 实体对象
    request : 请求对象
    """
    if request.method == 'POST':
        try:
            page_size = int(request.data.get('page_size', 50))
            page = int(request.data.get('page', 1))
        except (TypeError, ValueError):
            raise ValidationError('page and page_size must be integer!')
    else:
        try:
            page_size = int(request.GET.get('page_size', 50))
            page = int(request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise ValidationError('page and page_size must be integer!')

    list_len = obj_list.__len__()
    page_list = obj_list[page * page_size - page_size:page * page_size]
    ret_list = {
        'results': page_list,
        'count': list_len
    }
    return ret_list


def common_paging_bj(obj_list, request):
    """
    objs : 实体对象
    request : 请求对象
    """
    if request.method == 'POST':
        try:
            page_size = int(request.data.get('page_size', 50))
            page = int(request.data.get('page', 1))
        except (TypeError, ValueError):
            raise ValidationError('page and page_size must be integer!')
    else:
        try:
            page_size = int(request.GET.get('page_size', 50))
            page = int(request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise ValidationError('page and page_size must be integer!')

    list_len = obj_list.__len__()
    page_list = obj_list[page * page_size - page_size:page * page_size]
    ret_list = {
        'data': page_list,
        'count': list_len
    }
    return ret_list


def bf_paging(objs, request, Serializer):
    """
    objs : 实体对象
    request : 请求对象
    Serializer : 对应实体对象的序列化
    """
    try:
        page_size = int(request.GET.get('page_size', 50))
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        raise BFValidationError('page and page_size must be integer!')

    paginator = Paginator(objs, page_size)  # paginator对象
    total = paginator.num_pages  # 总页数
    try:
        objs = paginator.page(page)
    except PageNotAnInteger:
        objs = paginator.page(1)
    except EmptyPage:
        objs = paginator.page(paginator.num_pages)

    serializer = Serializer(objs, many=True)  # 序列化操作
    data = {
        'data': serializer.data,
        'page': page,
        'total': total
    }
    return data
