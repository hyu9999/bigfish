import logging

from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.questions.models import Question, QuestionKPRelationship
from bigfish.apps.questions.serializers import QuestionSerializer, \
    QuestionKPRelationshipSerializer
from bigfish.base import viewsets, status
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400

logger = logging.getLogger("django")


class QuestionKPRelationshipViewSet(viewsets.ModelViewSet):
    queryset = QuestionKPRelationship.objects.all()
    serializer_class = QuestionKPRelationshipSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_fields = ('id', 'unit', 'difficulty', 'question_type')

    def create(self, request, *args, **kwargs):
        data = request.data
        knowledge_data = data.get('knowledge_point')
        data['version'] = knowledge_data[:2]
        data['grade'] = knowledge_data[2:4]
        data['volume'] = knowledge_data[4:5]
        data['unit'] = knowledge_data[5:7]

        if data.get('show_type', None):
            if data['show_type'] == '1' or data['show_type'] == 1:
                data['show_type'] = "类型一"
            elif data['show_type'] == '2' or data['show_type'] == 2:
                data['show_type'] = "类型二"

        if data.get('option_type', None):
            op_type = data['option_type']
            if op_type == '1' or op_type == 1:
                data['option_type'] = "纯文字"
            elif op_type == '2' or op_type == 2:
                data['option_type'] = "纯图片"
            elif op_type == '3' or op_type == 3:
                data['option_type'] = "纯音频"

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        results = {"result": "success", "code": 200}
        return Response(rsp_msg_200(results), status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def analysis_knowledge(self, request, *args, **kwargs):
        """
        解析题目考察知识点
        """
        question_list = Question.objects.all()
        for ques in question_list:
            knowledge_data = ques.knowledge_point
            ques.version = knowledge_data[:2]
            ques.grade = knowledge_data[2:4]
            ques.volume = knowledge_data[4:5]
            ques.unit = knowledge_data[5:7]
            ques.save()
        data = {"result": "success", "code": 200}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def get_questions(self, request):
        """

        根据question_ids获取id下题目信息

        :param request: \n
            {"question_ids": [133, 134, 135]}

        :return: \n
        """
        question_id_list = request.data.get('question_ids', None)
        # 空值判断
        if not question_id_list:
            return Response(rsp_msg_400('题目id不能为空'), status=status.HTTP_200_OK)
        # 判断格式
        if not isinstance(question_id_list, list):
            return Response(rsp_msg_400('传入数据格式有误！'), status=status.HTTP_200_OK)
        # 查询题目信息
        questions_queryset = Question.objects.filter(id__in=question_id_list)
        if not questions_queryset.exists():
            return Response(rsp_msg_400('题目不存在'), status=status.HTTP_200_OK)
        data_list = QuestionSerializer(questions_queryset, many=True).data
        ret_data = []
        # 打乱题目返回顺序
        # random.shuffle(question_ids)
        for q_id in question_id_list:
            tmp_data = [x for x in data_list if x['id'] == int(q_id)]
            ret_data.extend(tmp_data)
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)
