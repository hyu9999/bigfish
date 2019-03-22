import logging
import os

from django.conf import settings
from bigfish.base import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.public.models import Public, AppTable, ATGroup
from bigfish.apps.public.serializers import PublicSerializer, AppTableSerializer, ATGroupSerializer
from bigfish.utils.functions import generate_file_name_windows
from bigfish.utils.operate_excel import export_excel
from bigfish.utils.query_freedom import get_model_fields_freedom, get_queryset_freedom, import_model_freedom, \
    import_serializer_freedom
from bigfish.base.ret_msg import rsp_msg_400, rsp_msg_200

logger = logging.getLogger('django')


class PublicViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a Public instance.
    list:
        Return all Public, ordered by most recently joined.
    create:
        Create a new Public.
    delete:
        Remove an existing Public.
    partial_update:
        Update one or more fields on an existing Public.
    update:
        Update a Public.
    """
    queryset = Public.objects.all()
    serializer_class = PublicSerializer

    @list_route(methods=['POST'])
    def common_export(self, request):
        """
        数据导出功能（支持xls和xlsx，默认为xlsx）

        :method: POST\n
        :param:\n
            {
            "app_name":"public",                                     # 模块名
            "model_name":"Public",                                   # 表名
            "query_condition":{},                                    # 查询条件
            "query_field_list":["id", "title", "content", "note1"],  # 导出字段
            "remove_field_list":["id"]                               # 排除字段(导出字段为空时生效)
            "suffix":"xlsx"                                          # 文件后缀 xls/xlsx
            }
            e.g.
            {
            "app_name":"public",
            "model_name":"Public",
            "query_condition":{},
            "query_field_list":["id", "title", "content", "note1"],
            "suffix":"xlsx"
            }
        :return:\n
            "http://192.168.1.110/media/2017-10-17_174448.540600.xls"
        """
        app_name = request.data.get('app_name', None)
        model_name = request.data.get('model_name', None)
        query_condition = request.data.get('query_condition', None)
        query_field_list = request.data.get('query_field_list', [])
        remove_field_list = request.data.get('remove_field_list', [])
        suffix = request.data.get('suffix', 'xlsx')
        field_dict = get_model_fields_freedom(app_name, model_name, query_field_list=query_field_list,
                                              remove_field_list=remove_field_list)
        val_list = get_queryset_freedom(app_name, model_name, query_condition, list(field_dict.keys()))
        filename = generate_file_name_windows(suffix)
        export_excel(val_list, field_dict, filename)
        url = "http://" + request.get_host() + settings.MEDIA_URL + filename
        return Response(url, status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def common_import(self, request):
        """
        数据导入功能（只支持xlsx格式）
        excel表头必须和数据库字段名称完全一样 否则读取不到
        请求方式：POST\n
        入参格式：\n
             {
            "app_name":"questions",                                  # 模块名
            "model_name":"question",                                 # 表名
            "query_field_list":["id", "version", "name", "content"], # 导出字段
            "url_path":"a.xlsx"
            }
            e.g.
             {
                "app_name":"shop",
                "model_name":"Wordhero",
                "query_field_list":["id", "name", "shield", "attack", "crit", "icon", "price", "freehero", "order"],
                "url_path":"a.xlsx"
             }
        出参格式：\n
            {"detail": "success", "code": 200}
        """
        app_name = request.data.get('app_name')
        model_name = request.data.get('model_name')
        query_field_list = request.data.get('query_field_list', [])
        url_path = request.data.get('url_path', None)
        exec_str = 'from bigfish.apps.{}.models import {}'.format(app_name, model_name)
        try:
            exec(exec_str)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)
        try:
            exec('from bigfish.utils.operate_excel import import_excel')
            # from bigfish.utils.operate_excel import import_excel
            ret_queryset = eval(
                'import_excel({0}, query_field_list={1}, url_path="{2}")'.format(model_name, query_field_list,
                                                                                 url_path))
            # ret_queryset = import_excel(model_name, query_field_list, url_path)
        except Exception as e:
            return Response(rsp_msg_400('导入错误：{}'.format(e)), status=status.HTTP_200_OK)

        exec_str = 'from bigfish.apps.{}.serializers import {}Serializer'.format(app_name, model_name)
        try:
            exec(exec_str)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)
        try:
            serializer_data = eval('{0}Serializer({1}, many=True).data'.format(model_name, ret_queryset))
        except Exception as e:
            logger.debug(e)
            serializer_data = {}
        return Response(rsp_msg_200("success", extra=serializer_data), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def create_fail_res(self, request):
        """
        :param request: {"title":"fail_res","note1":"http://.................."}title固定表明这个是错误资源，note1传入
        错误的资源地址
        :return:
        """
        title = request.data.get('title')
        res_url = request.data.get('note1')
        try:
            obj_old = Public.objects.get(note1=res_url)
        except:
            data_parmas = {
                'title': title,
                'note1': res_url
            }
            obj_new = Public.objects.create(**data_parmas)
        return Response(rsp_msg_200("success"), status=status.HTTP_200_OK)


class ATGroupViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Return a ATGroup instance.
        list:
            Return all ATGroup, ordered by most recently joined.
        create:
            Create a new ATGroup.
        delete:
            Remove an existing ATGroup.
        partial_update:
            Update one or more fields on an existing ATGroup.
        update:
            Update a ATGroup.
        """
    queryset = ATGroup.objects.all()
    serializer_class = ATGroupSerializer


class AppTableViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Return a AppTable instance.
        list:
            Return all AppTable, ordered by most recently joined.
        create:
            Create a new AppTable.
        delete:
            Remove an existing AppTable.
        partial_update:
            Update one or more fields on an existing AppTable.
        update:
            Update a AppTable.
        """
    queryset = AppTable.objects.all()
    serializer_class = AppTableSerializer

    @list_route(methods=['POST'])
    def exports(self, request):
        """
        数据导出功能（支持xls和xlsx，默认为xlsx）

        :method: POST\n
        :param:\n
            {
            "app_table_id":1,                                        # ID
            "query_condition":{},                                    # 查询条件
            "query_field_list":["id", "title", "content", "note1"],  # 导出字段
            "remove_field_list":["id"]                               # 排除字段(导出字段为空时生效)
            "suffix":"xlsx"                                          # 文件后缀 xls/xlsx
            }
            e.g.
            {
            "app_table_id":1,
            "query_condition":{},
            "query_field_list":["id", "title", "content", "note1"],
            "suffix":"xlsx"
            }
        :return:\n
            "http://192.168.1.110/media/2017-10-17_174448.540600.xls"
        """
        app_table_id = request.data.get('app_table_id', None)
        query_condition = request.data.get('query_condition', None)
        query_field_list = request.data.get('query_field_list', [])
        remove_field_list = request.data.get('remove_field_list', [])
        suffix = request.data.get('suffix', 'xls')
        try:
            app_table = AppTable.objects.get(id=app_table_id)
        except Exception as e:
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)
        field_dict = get_model_fields_freedom(app_table.app_name, app_table.table_name,
                                              query_field_list=query_field_list,
                                              remove_field_list=remove_field_list)
        val_list = get_queryset_freedom(app_table.app_name, app_table.table_name, query_condition,
                                        list(field_dict.keys()))
        filename = generate_file_name_windows(suffix)
        export_excel(val_list, field_dict, filename)
        url = "http://" + request.get_host() + settings.MEDIA_URL + filename
        return Response(rsp_msg_200(url), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def imports(self, request):
        """
        数据导入功能（只支持xlsx格式）

        请求方式：POST\n
        入参格式：\n
             {
            "app_table_id":1,                                        # 表名
            "query_field_list":["id", "version", "name", "content"], # 导出字段
            "url_path":"a.xlsx"
            }
            e.g.
             {
                "app_table_id":1,
                "query_field_list":["id", "name", "shield", "attack", "crit", "icon", "price", "freehero", "order"],
                "url_path":"a.xlsx"
             }
        出参格式：\n
            {"detail": "success", "code": 200}
        """
        app_table_id = request.data.get('app_table_id', None)
        try:
            app_table = AppTable.objects.get(id=app_table_id)
        except Exception as e:
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)
        query_field_list = request.data.get('query_field_list', [])
        url_path = request.data.get('url_path', None)
        exec_str = 'from bigfish.apps.{}.models import {}'.format(app_table.app_name, app_table.table_name)
        try:
            exec(exec_str)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)
        try:
            exec('from bigfish.utils.operate_excel import import_excel')
            ret_queryset = eval(
                'import_excel({0}, query_field_list={1}, url_path="{2}")'.format(app_table.table_name,
                                                                                 query_field_list,
                                                                                 url_path))
        except Exception as e:
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)

        exec_str = 'from bigfish.apps.{}.serializers import {}Serializer'.format(app_table.app_name,
                                                                                 app_table.table_name)
        try:
            exec(exec_str)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400(str(e)), status=status.HTTP_200_OK)
        try:
            serializer_data = eval('{0}Serializer({1}, many=True).data'.format(app_table.table_name, ret_queryset))
        except Exception as e:
            logger.debug(e)
            serializer_data = {}
        return Response(rsp_msg_200(serializer_data), status=status.HTTP_200_OK)
