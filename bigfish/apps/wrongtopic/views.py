from django.db.models import Q, Count
from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.knowledgepoint.models import KnowledgePoint
from bigfish.apps.knowledgepoint.views import get_knowledge_name
from bigfish.apps.textbooks.models import Textbook
from bigfish.apps.wrongtopic.models import WrongTopic, WrongTopicHis
from bigfish.apps.wrongtopic.serializers import WrongTopicSerializer, WrongTopicHisSerializer
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400


class WrongTopicViewSet(viewsets.ModelViewSet):
    queryset = WrongTopic.objects.all()
    serializer_class = WrongTopicSerializer


class WrongTopicHisViewSet(viewsets.ModelViewSet):
    queryset = WrongTopicHis.objects.all()
    serializer_class = WrongTopicHisSerializer

    @list_route(methods=['GET'])
    def wrongtopic_abstractpage(self, request):
        """
        错题本首页   \n
        :param request: {"textbook_id": } \n
        :return:
        """

        user = request.user
        result_list = []

        textbook_id = request.GET.get('textbook_id', None)
        if textbook_id is None:
            return Response(rsp_msg_400('请传入教材id'))
        topicqueryset = WrongTopic.objects.filter(~Q(master_level=6), publish_id=textbook_id, user_id=user.id)
        if topicqueryset.exists():
            for topic in topicqueryset:
                # 查询父级coding列表
                wrong_data = {}
                knowledge_coding_list = []
                knowledge_name_list = []
                try:
                    knowledge = KnowledgePoint.objects.get(coding=topic.kp_coding)
                except:
                    return Response(rsp_msg_400('知识点编码不存在'), status=status.HTTP_200_OK)
                knowledge_coding_list.append(knowledge.coding)
                knowledge_coding_list = get_knowledge_name(knowledge, knowledge_coding_list)
                knowledge_coding_list.reverse()
                for coding in knowledge_coding_list:
                    knowledge_info = KnowledgePoint.objects.get(coding=coding)
                    knowledge_name_list.append(knowledge_info.name)
                name = '-'.join(knowledge_name_list)
                wrong_data['knowledgepoint'] = name
                wrong_data['scene'] = topic.scene
                wrong_data['update_time'] = topic.update_time.strftime("%Y-%m-%d")
                wrong_data['question_id'] = topic.question.id
                result_list.append(wrong_data)
            result_list.sort(key=lambda e: (-e['update_time']))
        return Response(rsp_msg_200(result_list), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def abstractpage_pop(self, request):
        """
        错题本首页弹出 \n
        :param request: \n
        :return: \n
        """
        user = request.user
        result = []
        wrongtopic_queryset = WrongTopic.objects.filter(user_id=user.id, is_pop=True)
        if wrongtopic_queryset.exists():
            for wrongtopic in wrongtopic_queryset:
                # 拼接知识点名称
                knowledge_coding_list = []
                knowledge_name_list = []
                knowledge_data = {}
                knowledge = KnowledgePoint.objects.get(coding=wrongtopic.kp_coding)
                knowledge_coding_list.append(wrongtopic.kp_coding)
                knowledge_coding_list = get_knowledge_name(knowledge, knowledge_coding_list)
                knowledge_coding_list.reverse()
                for coding in knowledge_coding_list:
                    knowledge_info = KnowledgePoint.objects.get(coding=coding)
                    knowledge_name_list.append(knowledge_info.name)
                name = '-'.join(knowledge_name_list)
                knowledge_data['name'] = name
                knowledge_data['coding'] = wrongtopic.kp_coding
                result.append(knowledge_data)
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def update_abstractpage_pop(self, request):
        """
        修改首页弹出框数据状态 \n
        :param request: {"coding": []} \n
        :return: \n
        """
        user = request.user
        coding_list = request.data.get('coding', [])
        if len(coding_list) > 0:
            for coding in coding_list:
                try:
                    WrongTopic.objects.filter(user_id=user.id, kp_coding=coding).update(**{'is_pop': False})
                except:
                    raise BFValidationError('传入的coding有误')

        return Response(rsp_msg_200(), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def history_wrongtopic(self, request):
        """
        历史知识点 \n
        :param request: \n
        :return:
        """
        user = request.user
        result = []
        textbook_data = WrongTopic.objects.filter(~Q(master_level=6), user_id=user.id).values('publish_id').annotate(
            Count('kp_coding'))
        for textbook_info in list(textbook_data):
            textbook_dict = {}
            textbook_id = textbook_info['publish_id']
            try:
                textbook = Textbook.objects.get(id=textbook_id)
            except:
                return Response(rsp_msg_400('教材id不存在'))
            else:
                textbook_dict['bookgrade'] = textbook.bookgrade
                textbook_dict['icon'] = textbook.icon.url
                textbook_dict['count'] = textbook_info['kp_coding__count']
                textbook_dict['textbook_id'] = textbook_info['publish_id']
                result.append(textbook_dict)
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)