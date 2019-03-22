import logging

from django.db.models import Max
from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.knowledgepoint.models import KnowledgePoint
from bigfish.apps.knowledgepoint.serializers import KnowledgePointSerializer
from bigfish.apps.textbooks.models import Unit
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400

logger = logging.getLogger("django")


class KnowledgePointViewSet(viewsets.ModelViewSet):
    queryset = KnowledgePoint.objects.all()
    serializer_class = KnowledgePointSerializer

    def get_knowledge(self, knowledge_queryset):
        # 返回知识点数据
        result = []
        if knowledge_queryset.exists():
            for knowledge in knowledge_queryset:
                knowledge_data = get_knowledge_data(knowledge)
                result.append(knowledge_data)
        else:
            return Response(rsp_msg_400('知识点为空'), status=status.HTTP_200_OK)
        return result

    @list_route(methods=['GET'])
    def get_knowledgepoint(self, request):
        """
        获取知识点 \n
        :param request: coding:知识点编码 \n
        :return: \n
            {
                "data": {
                    "result": [
                        {
                            "has_children": false,
                            "unit_id": "2,3",
                            "knowledge": "代词",
                            "coding": "fb5e48b2-0481-4af2-bf9a-27bc40b7bdeb",
                            "parent_code": "424a7f13-4d21-485e-8628-bac64435c0ed",
                            "curriculum_standard": true,
                            "unit": "PEP4BUnit 2,PEP4BUnit 3",
                            "desc": ""
                        }
                    ]
                },
                "message": "success",
                "code": 200
            }
        """
        uuid = request.GET.get('coding', None)
        result = {}
        if uuid is None:
            knowledge_queryset = KnowledgePoint.objects.filter(parent_code=None).order_by('order')
            if knowledge_queryset.exists():
                result = self.get_knowledge(knowledge_queryset)
        else:
            knowledge_queryset = KnowledgePoint.objects.filter(parent_code=uuid).order_by('order')
            if knowledge_queryset.exists():
                result = self.get_knowledge(knowledge_queryset)
            else:
                return Response(rsp_msg_400('知识点没有子集'), status=status.HTTP_200_OK)
        return Response(rsp_msg_200({'result': result}), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def search_knowledge(self, request):
        """
        搜索知识点 \n
        :param request: {"knowledge": 知识点名称} \n
        :return:
        """
        knowledge_name = request.GET.get('knowledge', None)
        if knowledge_name is None:
            return Response(rsp_msg_400('请传入正确的知识点名称'), status=status.HTTP_200_OK)
        result = {}
        knowledge_name_data = []
        knowledge_queryset = KnowledgePoint.objects.filter(name__icontains=knowledge_name)
        if knowledge_queryset.exists():
            for knowledge in knowledge_queryset:
                knowledge_coding_list = []
                knowledge_name_list = []
                result_data = {}
                knowledge_coding_list.append(knowledge.coding)
                # 取父级coding列表
                knowledge_coding_list = get_knowledge_name(knowledge, knowledge_coding_list)
                knowledge_coding_list.reverse()
                for coding in knowledge_coding_list:
                    knowledge_info = KnowledgePoint.objects.get(coding=coding)
                    knowledge_name_list.append(knowledge_info.name)
                string = '-'.join(knowledge_name_list)
                result_data['knowledge_name'] = string
                result_data['coding'] = knowledge.coding
                knowledge_name_data.append(result_data)
                result['result'] = knowledge_name_data
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def remove_knowledge(self, request):
        """
        删除知识点 \n
        :param request: \n
        :return: \n
        """
        coding = request.data.get('coding', None)
        parent_coding = request.data.get('parent_code', None)
        son_coding_list = []
        son_coding_list.append(coding)
        son_coding_list = get_son_knowledge_coding(coding, son_coding_list)
        for son_coding in son_coding_list:
            try:
                knowledge = KnowledgePoint.objects.get(coding=son_coding)
            except:
                return Response(rsp_msg_400('coding不存在'), status=status.HTTP_200_OK)
            knowledge.delete()

        knowledge_queryset = KnowledgePoint.objects.filter(parent_code=parent_coding)
        if not knowledge_queryset.exists():
            knowledge = KnowledgePoint.objects.get(coding=parent_coding)
            knowledge.has_children = False
            knowledge.save()
        return Response(rsp_msg_200({'result': '删除成功'}), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def update_knowledge(self, request):
        """
        修改知识点 \n
        :param request:  \n
            {
              "curriculum_standard": true,
              "knowledge": "红色",
              "coding":"9d7a8b0f-4a6a-4b00-bcc8-12e2cae355ca",
              "unit": 2
              "parent_code": parent_code
              "desc": 描述
            }
        :return: \n

        """
        coding = request.data.get('coding', None)
        unit_string = request.data.get('unit_id', '')
        curriculum_standard = request.data.get('curriculum_standard', False)
        name = request.data.get('knowledge', None)
        parent_code = request.data.get('parent_code', None)
        desc = request.data.get('desc', '')
        drag = request.data.get('drag', False)  # 判断是否是拖拽
        old_parent_code = request.data.get('old_parent_code', None)
        user = request.user
        if unit_string == '':
            unit_list = []
        else:
            unit_list = unit_string.split(',')
        if name is None:
            return Response(rsp_msg_400('知识点名称不能为空'), status=status.HTTP_200_OK)
        if drag:
            if parent_code == '':
                parent_code = None
            knowledge_coding_list = []
            knowledge_order = KnowledgePoint.objects.filter(parent_code=parent_code).aggregate(Max('order'))
            if knowledge_order['order__max'] is None:
                knowledge_order['order__max'] = 0
            data = {'curriculum_standard': curriculum_standard, 'parent_code': parent_code,
                    'desc': desc, 'order': knowledge_order['order__max'] + 1, 'update_user': user.username}
            # 修改根节点名称和层级字段
            try:
                knowledge = KnowledgePoint.objects.get(coding=parent_code)
            except:
                # 拖拽到最上层
                data.update({'root': name, 'level': 1})
            else:
                if knowledge.has_children == False:
                    knowledge.has_children = True
                    knowledge.save()
                knowledge_coding_list.append(knowledge.coding)
                knowledge_coding_list = get_knowledge_name(knowledge, knowledge_coding_list)
            if len(knowledge_coding_list) > 0:
                root_coding = knowledge_coding_list[-1]
                root_knowledge = KnowledgePoint.objects.get(coding=root_coding)
                data.update({'root': root_knowledge.name, 'level': len(knowledge_coding_list) + 1})
            # 变更子级的level
            update_level(coding, data['level'])
        else:
            data = {'name': name, 'curriculum_standard': curriculum_standard, 'desc': desc,
                    'update_user': user.username}
        try:
            KnowledgePoint.objects.filter(coding=coding).update(**data)
            knowledge_info = KnowledgePoint.objects.get(coding=coding)
            # if len(unit_list) != 0:
            unit_list = [unit_id for unit_id in map(int, unit_list)]
            try:
                unit_queryset = Unit.objects.filter(id__in=unit_list)
            except:
                return Response(rsp_msg_400('单元id不存在'), status=status.HTTP_200_OK)
            knowledge_info.unit = unit_queryset
            knowledge_info.save()
        except Exception as e:
            return Response(rsp_msg_400('修改知识点单元错误'), status=status.HTTP_200_OK)
        # 修改旧父集的has_children的值
        if old_parent_code is not None:
            try:
                parent_knowledge = KnowledgePoint.objects.get(coding=old_parent_code)
            except:
                return Response(rsp_msg_400('旧父集编码不存在'), status=status.HTTP_200_OK)
            knowledge_queryset = KnowledgePoint.objects.filter(parent_code=old_parent_code)
            if knowledge_queryset.exists():
                parent_knowledge.has_children = True
                parent_knowledge.save()
            else:
                parent_knowledge.has_children = False
                parent_knowledge.save()
        return Response(rsp_msg_200({'result': '数据修改成功'}), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def add_knowledge(self, request):
        """
        添加知识点, 添加第一层时不传 parent_code参数 \n
        :param request: \n
            {
              "curriculum_standard": true,
              "knowledge": "黑色",
              "parent_code":"9f8b82af-c280-455f-b84c-bbc152961218",
              "unit_id": "3",
              "desc": 描述
            }
        :return: \n
            {
              "data": {
                "result": "知识点添加成功"
                },
              "message": "success",
              "code": 200
            }
        """
        user = request.user
        unit_list = request.data.get('unit_id', "")
        curriculum_standard = request.data.get('curriculum_standard', False)
        name = request.data.get('knowledge', '')
        parent_code = request.data.get('parent_code', None)
        desc = request.data.get('desc', '')
        knowledge_data = {'name': name, 'curriculum_standard': curriculum_standard,
                          'parent_code': parent_code, 'update_user': user.username, 'desc': desc}
        knowledge_coding_list = []
        if unit_list == "":
            unit_list = []
        else:
            unit_list = unit_list.split(',')
        # 添加首层
        if parent_code is None:
            knowledge_order = KnowledgePoint.objects.filter(parent_code=None).aggregate(Max('order'))
            if knowledge_order['order__max'] is None:
                knowledge_order['order__max'] = 0
            knowledge_data.update({'root': name, 'level': 1, 'order': knowledge_order['order__max'] + 1})
            knowledge = KnowledgePoint.objects.create(**knowledge_data)

            for unit_id in unit_list:
                unit_id = int(unit_id)
                try:
                    unit = Unit.objects.get(id=unit_id)
                except:
                    return Response(rsp_msg_400('单元id不存在'), status=status.HTTP_200_OK)
                knowledge.unit.add(unit)
                knowledge.save()
            knowledge_dict = get_knowledge_data(knowledge)
            return Response(rsp_msg_200(knowledge_dict), status=status.HTTP_200_OK)

        try:
            parent_knowledge = KnowledgePoint.objects.get(coding=parent_code)
        except:
            raise BFValidationError('父级知识点编码错误')
        else:
            parent_knowledge.has_children = True
            parent_knowledge.save()
        try:
            knowledge = KnowledgePoint.objects.get(coding=parent_code)
        except:
            raise BFValidationError('父级知识点编码错误')
        else:
            if knowledge.has_children == False:
                knowledge.has_children = True
                knowledge.save()
            knowledge_coding_list.append(knowledge.coding)
            knowledge_coding_list = get_knowledge_name(knowledge, knowledge_coding_list)
        if len(knowledge_coding_list) > 0:
            root_coding = knowledge_coding_list[-1]
            root_knowledge = KnowledgePoint.objects.get(coding=root_coding)
            knowledge_data.update({'root': root_knowledge.name, 'level': len(knowledge_coding_list) + 1})
        order_data = KnowledgePoint.objects.filter(parent_code=parent_code).aggregate(Max('order'))
        if order_data['order__max'] is None:
            order_data['order__max'] = 0
        knowledge_data.update({'order': order_data['order__max'] + 1})
        knowledge_info = KnowledgePoint.objects.create(**knowledge_data)
        for unit_id in unit_list:
            unit_id = int(unit_id)
            try:
                unit = Unit.objects.get(id=unit_id)
            except:
                return Response(rsp_msg_400('单元id不存在'), status=status.HTTP_200_OK)
            knowledge_info.unit.add(unit)
            knowledge_info.save()
        knowledge_dict = get_knowledge_data(knowledge)
        return Response(rsp_msg_200(knowledge_dict), status=status.HTTP_200_OK)

    @list_route()
    def get_unit_name(self, request):
        """
        获取单元名称 \n
        :param request: {"unit_id": 2} \n
        :return: \n
           {
              "code": 200,
              "data": {
                "unit_data": [
                  {
                    "unit_id": 1,
                    "unit": "PEP4BUnit 1"
                  },
                  ]
              },
              "message": "success"
            }
        """
        unit_id = request.GET.get('unit_id', None)
        result = {}
        unit_list = []
        if unit_id is None:
            unit_queryset = Unit.objects.filter(is_active=True).order_by('id')
            if unit_queryset.exists():
                for unit in unit_queryset:
                    unit_data = {}
                    unit_data['unit_id'] = unit.id
                    unit_data['unit'] = unit.textbook.title + unit.title
                    unit_list.append(unit_data)
                result['unit_data'] = unit_list
            return Response(rsp_msg_200(result), status=status.HTTP_200_OK)
        try:
            unit = Unit.objects.get(id=unit_id)
        except:
            return Response(rsp_msg_400('单元id不存在'), status=status.HTTP_200_OK)
        else:
            result['unit'] = unit.textbook.title + unit.title
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)


def get_knowledge_name(knowledge, coding):
    # 递归拿取父级coding列表
    # 注意：只能拿去父级的coding列表，不包括当前知识点coding
    if knowledge.parent_code == None:
        return coding
    else:
        try:
            knowledge = KnowledgePoint.objects.get(coding=knowledge.parent_code)
        except:
            raise BFValidationError('知识点参数有误')
        else:
            coding.append(knowledge.coding)
            return get_knowledge_name(knowledge, coding)


def update_level(coding, level):
    # 迭代更新拖拽后子集的level
    knowledge_queryset = KnowledgePoint.objects.filter(parent_code=coding)
    if knowledge_queryset.exists():
        for knowledge in knowledge_queryset:
            knowledge.level = level + 1
            knowledge.save()
            update_level(knowledge.coding, knowledge.level)
    return 1


def get_son_knowledge_coding(coding, son_coding_list):
    """
    迭代删除当前知识点下的子节点
    :param coding:
    :return:
    """
    knowledge_queryset = KnowledgePoint.objects.filter(parent_code=coding)
    if knowledge_queryset.exists():
        for knowledge in knowledge_queryset:
            son_coding_list.append(knowledge.coding)
            get_son_knowledge_coding(knowledge.coding, son_coding_list)
    return son_coding_list


def get_knowledge_data(knowledge):
    """
    返回知识点的拼接数据
    :param knowledge:
    :return:
    """
    knowledge_data = {}
    unit_id_list = []
    unit_name_list = []
    knowledge_data['knowledge'] = knowledge.name
    knowledge_data['coding'] = knowledge.coding
    knowledge_data['curriculum_standard'] = knowledge.curriculum_standard
    knowledge_data['has_children'] = knowledge.has_children
    knowledge_data['desc'] = knowledge.desc
    knowledge_data['parent_code'] = knowledge.parent_code
    unit_queryset = knowledge.unit.all()
    for unit in unit_queryset:
        unit_id_list.append(str(unit.id))
        unit_name_list.append(unit.textbook.title + unit.title)
    unit_id = ','.join(unit_id_list)
    unit_name = ','.join(unit_name_list)
    knowledge_data['unit_id'] = unit_id
    knowledge_data['unit'] = unit_name
    return knowledge_data
