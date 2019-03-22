import random

from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from bigfish.apps.bfwechat.models import WxUserRelationship
from bigfish.apps.homework.models import Homework, PushRecord, ReceiveRecord
from bigfish.apps.intelligentpush.models import IntelligentPush, PushQuestions
from bigfish.apps.textbooks.models import Textbook
from bigfish.apps.users.models import BigfishUser, UserKlassRelationship
from bigfish.apps.wrongtopic.models import WrongTopic, WrongTopicHis
from bigfish.apps.intelligentpush.serializers import IntelligentPushSerializer
from bigfish.apps.questions.models import Question, QuestionKPRelationship
from bigfish.apps.knowledgepoint.views import get_knowledge_name
from bigfish.apps.knowledgepoint.models import KnowledgePoint
from bigfish.apps.classrooms.models import Classroom

from bigfish.apps.schools.models import Klass
from bigfish.settings.base import WEHOST
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400


class IntelligentPushViewSet(viewsets.ModelViewSet):
    queryset = IntelligentPush.objects.all()
    serializer_class = IntelligentPushSerializer

    @list_route(methods=['GET'])
    def comprehensive_refresher(self, request):
        """
        综合复习 \n
        :param request:{"textbook_id": 14} \n
        :return: \n
        """
        user = request.user
        textbook_id = request.GET.get('textbook_id', None)
        if textbook_id is None:
            return Response(rsp_msg_400('请传入教材id'), status=status.HTTP_200_OK)
        # 组题完成列表
        group_question_list = []
        wrong_queryset = WrongTopic.objects.filter(user_id=user.id, textbook_id=textbook_id).order_by('create_time')
        if wrong_queryset.exists():
            # 组题
            group_question_list = push_question(request, wrong_queryset, 1)

        # 返回题目信息
        result = []
        for question_id in group_question_list:
            result_dict = {}
            result_list = []
            knowledge_relationship_queryset = QuestionKPRelationship.objects.filter(question_id=question_id).order_by('order', 'seconds')
            for knowledge_relationship in knowledge_relationship_queryset:
                knowledge_data = {}
                knowledge_name_list = []
                coding = [knowledge_relationship.knowledge_point.coding]
                knowledge_coding_list = get_knowledge_name(knowledge_relationship.knowledge_point, coding)
                knowledge_coding_list.reverse()
                for coding in knowledge_coding_list:
                    knowledge_info = KnowledgePoint.objects.get(coding=coding)
                    knowledge_name_list.append(knowledge_info.name)
                name = '-'.join(knowledge_name_list)
                knowledge_data['name'] = name
                knowledge_data['coding'] = knowledge_relationship.knowledge_point.coding
                knowledge_data['index'] = knowledge_relationship.order
                try:
                    wrongtopic = WrongTopic.objects.get(kp_coding=knowledge_relationship.knowledge_point.coding, user_id=user.id)
                except:
                    # 表示知识点没有加入过错题本
                    knowledge_data['master_level'] = 0
                else:
                    knowledge_data['master_level'] = wrongtopic.master_level
                result_list.append(knowledge_data)
            result_dict['id'] = question_id
            result_dict['knowledge_data'] = result_list
            result.append(result_dict)
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route()
    def task_question_push(self, request):
        """
        课堂知识巩固 \n
        :param request: {"task_id": } \n
        :return: \n
        """
        user = request.user
        classroom_id = request.GET.get('classroom_id', None)
        if classroom_id is None:
            return Response(rsp_msg_400('请传入课堂id'), status=status.HTTP_200_OK)

        wrong_queryset = WrongTopic.objects.filter(user_id=user.id, classroom_id=classroom_id).order_by('id')
        if wrong_queryset.exists():
            group_question_list = push_question(request, wrong_queryset, 2)
            # 题目不够用活动内知识点补到5道题
            if len(group_question_list) < 5:
                question_list = task_push_question(request, push_type=2, classroom_id=classroom_id, is_homework=False)[: 5 - len(group_question_list)]
                group_question_list.extend(question_list)
        # 活动中没有做错题
        else:
            group_question_list = task_push_question(request, push_type=2, classroom_id=classroom_id, is_homework=False)

        # question_str = ','.join([question_id for question_id in map(str, group_question_list)])
        return Response(rsp_msg_200(group_question_list), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def individuation_homework_student(self, request):
        """
        个性化作业学生列表 \n
        :param request: {"klass_id": 1} \n
        :return: \n
        """
        klass_id = request.GET.get('klass_id')
        result = {}
        user_data = []
        try:
            klass = Klass.objects.get(id=klass_id)
        except:
            raise BFValidationError('班级id不存在')
        else:
            user_queryset = klass.person.filter(identity='学生')
            result['klass_name'] = klass.grade + klass.name
        for user in user_queryset:
            user_info = {}
            user_info['icon'] = user.icon
            user_info['relname'] = user.realname
            user_info['user_id'] = user.user_id
            try:
                WxUserRelationship.objects.get(student__id=user.user.id)
            except:
                user_info['bound_state'] = False
            else:
                user_info['bound_state'] = True
            user_data.append(user_info)
        result['user_data'] = user_data
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_individuation_homework(self, request):
        """
        展示个性作业数据 \n
        :param request: \n
        :return:
        """

        klass_id = request.GET.get('klass_id', None)
        result = []
        try:
            klass = Klass.objects.get(id=klass_id)
        except:
            raise BFValidationError('班级id不存在')
        else:
            user_queryset = klass.person.filter(identity="学生")
        for user in user_queryset:
            question_data = {}
            try:
                WxUserRelationship.objects.get(student=user.user)
            except:
                continue
            classroom = Classroom.objects.filter(klass_id=klass_id).order_by('-finish_time').first()
            if classroom is None:
                return Response(rsp_msg_400('该班级没有开启过活动'), status=status.HTTP_200_OK)
            wrong_queryset = WrongTopicHis.objects.filter(~Q(master_level=6), user_id=user.user_id, task_id=classroom.id)
            # 获取组提列表
            group_question_list = push_homework_question(request, wrong_queryset, 3, classroom.id, user)
            if isinstance(group_question_list, str):
                return Response(rsp_msg_200(group_question_list), status=status.HTTP_200_OK)
            if isinstance(group_question_list, list) and group_question_list:
                group_question_str = ','.join(map(str, group_question_list))
                question_data['user_id'] = user.user.id
                question_data['question_list'] = group_question_str
                result.append(question_data)
                create_intelligentpush(request, group_question_list, push_type=3, is_homework=True)
        return Response(rsp_msg_200(result), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def intelligentpush_homework(self, request):
        """
        发布个性化,巩固作业 \n
        :param request:
        :return:
        """
        # 个性作业
        question_data = request.data.get('question_data')
        if isinstance(question_data, list):
            question_dict = {}
            for question_info in question_data:
                question_dict[question_info['user_id']] = question_info['question_list']
            create_homework(request=request, question_dict=question_dict)
        # 巩固作业
        elif isinstance(question_data, str):
            if question_data == '':
                question_list = []
            else:
                question_list = [{'questionId': question_id} for question_id in map(int, question_data.split(','))]
            create_homework(request, question_data=question_list)
        return Response(rsp_msg_200(), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_cement_homework(self, request):
        """
        展示巩固作业 \n
        :param request: {"klass_id":}\n
        :return:  \n
        """

        klass_id = request.GET.get('klass_id', None)
        question_id_list = []
        knowledge_list = []
        # 获取最近任务中练习活动中知识点
        task_queryset = Classroom.objects.filter(klass_id=klass_id).order_by('-close_date')
        if task_queryset is None:
            raise BFValidationError('该班级没有创建过任务')
        for task in task_queryset:
            activity_queryset = task.activity.filter(pointer='student_test')
            if activity_queryset.exists():
                for activity in activity_queryset:
                    question_id_list.extend(activity.question_ids.split(','))
            else:
                continue
            for question_id in question_id_list:
                knowledge_queryset = Question.objects.get(id=question_id).knowledge_point.all()
                if knowledge_queryset.exists():
                    for knowledge in knowledge_queryset:
                        knowledge_list.append(knowledge)
            if len(knowledge_list) == 0:
                continue
            break
        # 组题列表总和
        question_sum_list = []
        # 组题完成列表
        group_question_list = []
        # 普通题列表
        common_question_sum_list = []
        # 推送题列表
        push_question_sum_list = []

        # 取出知识点
        for knowledge in knowledge_list:
            push_question_list = knowledge.questions_question_knowledge_point.filter(is_push=True).values_list(
                'id', flat=True)
            common_question_list = knowledge.questions_question_knowledge_point.filter(
                is_push=False).values_list('id', flat=True)
            common_question_sum_list.extend(list(common_question_list))
            push_question_sum_list.extend(list(push_question_list))
        push_question_sum_list = list(set(push_question_sum_list))
        common_question_sum_list = list(set(common_question_sum_list))
        # 知识点数量
        knowledge_num = len(knowledge_list)
        if knowledge_num <= 10:
            if len(push_question_sum_list) >= 10:
                group_question_list = random.sample(push_question_sum_list, 10)
            elif len(push_question_sum_list) < 10:
                if len(common_question_sum_list) > 10 - len(push_question_sum_list):
                    group_question_list.extend(push_question_sum_list)
                    group_question_list.extend(random.sample(common_question_sum_list, 10 - len(push_question_sum_list)))
                    # group_question_list = random.sample(common_question_sum_list, 10 - len(push_question_sum_list))
                else:
                    group_question_list.extend(push_question_sum_list)
                    group_question_list.extend(random.sample(common_question_sum_list, len(common_question_sum_list)))
                    # group_question_list = random.sample(common_question_sum_list, len(common_question_sum_list))
        elif knowledge_num > 10:
            for knowledge in knowledge_list:
                push_question_list = knowledge.questions_question_knowledge_point.filter(is_push=True).values_list('id', flat=True)
                # 每个知识点取一道题
                if push_question_list:
                    question_sum_list.extend(random.sample(list(push_question_list), 1))
            question_sum_list = list(set(question_sum_list))
            group_question_list = question_sum_list[:10]
        # 记录推送题
        create_intelligentpush(request, group_question_list, push_type=4, is_homework=True)
        # group_question_str = ','.join(map(str, group_question_list))
        return Response(rsp_msg_200(group_question_list), status=status.HTTP_200_OK)


def push_homework_question(request, wrongtopic_queryset, push_type, task_id, user):
    """个性化作业组题"""

    # 组题列表总和
    question_sum_list = []
    # 组题完成列表
    group_question_list = []
    # 普通题列表
    common_question_sum_list = []
    # 推送题列表
    push_question_sum_list = []
    for wrong in wrongtopic_queryset:
        try:
            knowledge = KnowledgePoint.objects.get(coding=wrong.kp_coding)
        except:
            return '知识点不存在'
        else:
            push_question_list = knowledge.questions_question_knowledge_point.filter(is_push=True).values_list('id',
                                                                                                               flat=True)
            common_question_list = knowledge.questions_question_knowledge_point.filter(is_push=False).values_list('id',
                                                                                                                  flat=True)
            common_question_sum_list.extend(list(common_question_list))
            push_question_sum_list.extend(list(push_question_list))
    push_question_sum_list = list(set(push_question_sum_list))
    common_question_sum_list = list(set(common_question_sum_list))
    # 错题本知识点数量
    knowledge_num = len(wrongtopic_queryset)
    if knowledge_num <= 10:
        if len(push_question_sum_list) >= 10:
            group_question_list = random.sample(push_question_sum_list, 10)
        elif len(push_question_sum_list) < 10:
            if len(common_question_sum_list) > 10 - len(push_question_sum_list):
                group_question_list.extend(push_question_sum_list)
                group_question_list.extend(random.sample(common_question_sum_list, 10 - len(push_question_sum_list)))
            else:
                group_question_list.extend(push_question_sum_list)
                group_question_list.extend(random.sample(common_question_sum_list, len(common_question_sum_list)))
        if len(group_question_list) < 10:
            # wrong_queryset = WrongTopicHis.objects.filter(master_level=6, user_id=user.user_id, task_id=task_id)
            # for wrong in wrong_queryset:
            #     try:
            #         knowledge = KnowledgePoint.objects.get(coding=wrong.kp_coding)
            #     except:
            #         return '知识点不存在'
            #     else:
            #         task_push_question_list = knowledge.questions_question_knowledge_point.filter(
            #             is_push=True).values_list('id', flat=True)
            #         task_common_question_list = knowledge.questions_question_knowledge_point.filter(
            #             is_push=False).values_list('id', flat=True)
            #         group_question_list.extend(task_push_question_list)
            #         group_question_list.extend(task_common_question_list)
            question_list = task_push_question(request, push_type=3, task_id=task_id, is_homework=True)
            group_question_list.extend(question_list[:10-len(group_question_list)])
        if len(group_question_list) < 10:
            wrong_queryset = WrongTopic.objects.filter(~Q(master_level=6), user_id=user.user_id).order_by('-update_time')
            for wrong in wrong_queryset:
                try:
                    knowledge = KnowledgePoint.objects.get(coding=wrong.kp_coding)
                except:
                    return '知识点不存在'
                else:
                    task_push_question_list = knowledge.questions_question_knowledge_point.filter(
                        is_push=True).values_list('id', flat=True)
                    group_question_list.extend(task_push_question_list)
                    group_question_list = list(set(group_question_list))
                    if group_question_list == 10:
                        break
    elif knowledge_num > 10:
        for wrong in wrongtopic_queryset:
            try:
                knowledge = KnowledgePoint.objects.get(coding=wrong.kp_coding)
            except:
                # 没有错误知识点
                push_question_list = []
            else:
                push_question_list = knowledge.questions_question_knowledge_point.filter(
                    is_push=True).values_list('id', flat=True)
            # 每个知识点取一道题
            if push_question_list:
                question_sum_list.extend(random.sample(list(push_question_list), 1))
        question_sum_list = list(set(question_sum_list))
        group_question_list = question_sum_list[:10]
    group_question_list = list(set(group_question_list[:10]))
    # create_intelligentpush(request=request, group_question_list=group_question_list, push_type=push_type, is_homework=True)
    return group_question_list


def push_question(request, wrongtopic_queryset, push_type):
    """综合复习，课堂巩固组题"""

    # 组题列表总和
    question_sum_list = []
    # 组题完成列表
    group_question_list = []
    # 普通题列表
    common_question_sum_list = []
    # 知识点推送题列表总和
    push_question_sum_list = []
    for wrong in wrongtopic_queryset:

        try:
            knowledge = KnowledgePoint.objects.get(coding=wrong.kp_coding)
        except:
            raise BFValidationError('知识点不存在')
        else:
            push_question_list = knowledge.questions_question_knowledge_point.filter(is_push=True).values_list('id',
                                                                                                               flat=True)
            common_question_list = knowledge.questions_question_knowledge_point.filter(is_push=False).values_list('id',
                                                                                                                  flat=True)
            common_question_sum_list.extend(list(common_question_list))
            push_question_sum_list.extend(list(push_question_list))
    # 错题本知识点数量
    push_question_sum_list = list(set(push_question_sum_list))
    common_question_sum_list = list(set(common_question_sum_list))
    knowledge_num = len(wrongtopic_queryset)
    if knowledge_num <= 5:
        if len(push_question_sum_list) >= 5:
            group_question_list = random.sample(push_question_sum_list, 5)
        elif len(push_question_sum_list) < 5:
            if len(common_question_sum_list) > 5 - len(push_question_sum_list):
                group_question_list.extend(push_question_sum_list)
                # group_question_list = random.sample(common_question_sum_list, 5 - len(push_question_sum_list))
                group_question_list.extend(random.sample(common_question_sum_list, 5 - len(push_question_sum_list)))
            else:
                group_question_list.extend(push_question_sum_list)
                # group_question_list = random.sample(common_question_sum_list, len(common_question_sum_list))
                group_question_list.extend(random.sample(common_question_sum_list, len(common_question_sum_list)))
    elif knowledge_num > 5:
        for wrong in wrongtopic_queryset:
            try:
                knowledge = KnowledgePoint.objects.get(coding=wrong.kp_coding)
            except:
                # 没有错误知识点
                push_question_list = []
            else:
                push_question_list = knowledge.questions_question_knowledge_point.filter(
                    is_push=True).values_list('id', flat=True)
            # 每个知识点取一道题
            if push_question_list:
                question_sum_list.extend(random.sample(list(push_question_list), 1))
        question_sum_list = list(set(question_sum_list))
        group_question_list = question_sum_list[:5]
    create_intelligentpush(request, group_question_list, push_type, is_homework=False)
    return group_question_list


def task_push_question(request, push_type, classroom_id, is_homework):
    """获取任务中活动题关联知识点的推送题"""
    group_question_list = []
    question_id_sum = []
    knowledge_set = []
    classroom = Classroom.objects.get(id=classroom_id)
    # 查询练习活动
    activity_queryset = classroom.activity.act_type.filter(first_type=1)
    for activity in activity_queryset:
        question_id_list = activity.rule['question']
        question_id_sum.extend(question_id_list)
    # 获取所有知识点
    for question_id in question_id_sum:
        knowledge_queryset = list(Question.objects.get(id=question_id).knowledge_point.all())
        knowledge_set.extend(knowledge_queryset)
    random.shuffle(knowledge_set)
    for knowledge in knowledge_set:
        question = Question.objects.filter(is_push=True, knowledge_point=knowledge).first()
        group_question_list.append(question.id)
    group_question_list = list(set(group_question_list))[:5]
    create_intelligentpush(request, group_question_list, push_type, is_homework=is_homework)
    return group_question_list


def create_intelligentpush(request, group_question_list, push_type, is_homework=False):
    # 智能推送记录存储
    intelligent = {}
    pushquestions = {}
    user = request.user
    try:
        klass = UserKlassRelationship.objects.get(user=user, is_default=True)
    except Exception as e:
        raise BFValidationError("获取用户班级失败！")
    user_data = {'user_id': user.id, 'username': user.username, 'realname': user.profile.realname,
                 'nickname': user.profile.nickname, 'areas_code': klass.school.areas.adcode,
                 'areas_name': klass.school.areas.__str__(), 'school_id': klass.school.id,
                 'school_name': klass.school.name, 'klass_id': klass.id, 'klass_name': klass.name}
    intelligent.update(user_data)
    intelligent.update({'push_type': push_type, 'push_user': user.id, 'is_homework': is_homework})
    pushquestions.update(user_data)
    pushquestions.update({'push_type': push_type, 'is_homework': is_homework})
    if push_type == 1:
        # 综合复习
        textbook_id = request.GET.get('textbook', None)
        if textbook_id is None:
            return Response(rsp_msg_400('请传入教材ID'))
        textbook = Textbook.objects.get(id=textbook_id)
        intelligent.update({'publish_id': textbook_id, 'publish_name': textbook.title, 'term_num': textbook.term_num})
        intelligentpush = IntelligentPush.objects.create(**intelligent)
        # 存储智能推送题目数据
        pushquestions.update({'intelligent_push': intelligentpush, 'publish_id': textbook_id, 'publish_name': textbook.title,
                              'term_num': textbook.term_num})
        for question_id in group_question_list:
            try:
                question = Question.objects.get(id=question_id)
            except:
                raise BFValidationError('题目id有误')
            else:
                pushquestions.update({'push_user': user.id, 'question_id': question_id, 'question_content': question.content})
            PushQuestions.objects.create(**pushquestions)
    elif push_type == 2:
        # 课堂知识巩固
        classroom_id = request.GET.get('classroom_id', None)
        try:
            classroom = Classroom.objects.get(id=classroom_id)
        except:
            raise BFValidationError('传入的任务id不存在')
        else:
            intelligent.update({})
            intelligentpush = IntelligentPush.objects.create(**intelligent)
            pushquestions.update({})
            for question_id in group_question_list:
                try:
                    question = Question.objects.get(id=question_id)
                except:
                    raise BFValidationError('题目id有误')
                else:
                    pushquestions.update({'push_user': user.id, 'question_id': question_id, 'question_content': question.content})
                PushQuestions.objects.create(**pushquestions)
    # elif push_type == 3:
    #     # 个性作业
    #     try:
    #         task = Task.objects.filter(user__id=user.id).order_by('-close_date').first()
    #     except Exception as e:
    #         return e
    #     intelligent.update(
    #         {'task_id': task.id, 'task_name': task.name, 'unit_id': task.unit.id, 'unit_name': task.unit.title,
    #          'term_num': task.unit.textbook.term_num, 'lesson_id': task.lesson.id, 'lesson_name': task.lesson.title})
    #     # intelligentpush, variable = IntelligentPush.objects.get_or_create(**intelligent)
    #     intelligentpush = IntelligentPush.objects.create(**intelligent)
    #     pushquestions.update({'intelligent_push': intelligentpush, 'task_id': task.id, 'task_name': task.name,
    #                           'unit_id': task.unit.id, 'unit_name': task.unit.title,
    #                           'term_num': task.unit.textbook.term_num, 'lesson_id': task.lesson.id,
    #                           'lesson_name': task.lesson.title})
    #     for question_id in group_question_list:
    #         try:
    #             question = Question.objects.get(id=question_id)
    #         except:
    #             raise BFValidationError('题目id有误')
    #         else:
    #             pushquestions.update({'push_user': user.id, 'question_id': question_id,
    #  'question_content': question.content})
    #         PushQuestions.objects.create(**pushquestions)
    # elif push_type == 4:
    #     # 巩固性作业
    #     klass_id = request.GET.get('klass_id', None)
    #     # 获取最近任务中练习活动中知识点
    #     task = Task.objects.filter(klass_id=klass_id).order_by('close_date').first()
    #     intelligent.update({'task_id': task.id, 'task_name': task.name, 'unit_id': task.unit.id, 'unit_name': task.unit.title,
    #                         'term_num': task.unit.textbook.term_num, 'lesson_id': task.lesson.id, 'lesson_name': task.lesson.title})
    #     intelligentpush = IntelligentPush.objects.create(**intelligent)
    #     pushquestions.update({'intelligent_push': intelligentpush, 'task_id': task.id, 'task_name': task.name,
    #                           'unit_id': task.unit.id, 'unit_name': task.unit.title,
    #                           'term_num': task.unit.textbook.term_num, 'lesson_id': task.lesson.id,
    #                           'lesson_name': task.lesson.title})
    #     for question_id in group_question_list:
    #         try:
    #             question = Question.objects.get(id=question_id)
    #         except:
    #             raise BFValidationError('题目id有误')
    #         else:
    #             pushquestions.update({'push_user': user.id, 'question_id': question_id, 'question_content': question.content})
    #         PushQuestions.objects.create(**pushquestions)
    return group_question_list


def create_homework(request, question_data=[], question_dict={}):
    """创建个性化，巩固作业"""
    user = request.user
    klass_id = request.data.get('klass_id', None)
    # 作业题目是否相同
    question_alike = request.data.get('question_alike', True)
    errors = []
    if not klass_id:
        errors.append({"message": "班级id为必须传入字段！"})
        return Response(rsp_msg_400(errors), status=status.HTTP_200_OK)
    try:
        Klass.objects.get(id=klass_id)
    except:
        return Response(rsp_msg_400('该班级不存在'))
    data_parmas = {
        'user_id': user.id,
        'question_data': question_data,
    }
    task_obj = Homework.objects.create(**data_parmas)
    # queryset = UserProfile.objects.filter(default_cid=klass_id, identity="学生")
    queryset = Klass.objects.get(id=klass_id).person.filter(identity="学生")
    if queryset.count() == 0:
        return Response(rsp_msg_200({'user_list': []}), status=status.HTTP_200_OK)
    user_list = queryset.values_list('user__id', flat=True)
    with transaction.atomic():
        tpr = PushRecord.objects.create(
            **{'push_user': user, 'task': task_obj, 'is_active': True, 'klass': klass_id})
        sql_list = []
        if question_alike:
            for user_id in user_list:
                data_dict = {'task_push_record': tpr, 'user_id': user_id}
                sql = ReceiveRecord(**data_dict)
                sql_list.append(sql)
            ReceiveRecord.objects.bulk_create(sql_list)
            task_obj.push_num = task_obj.push_num + 1
            task_obj.save()
            # 推送信息
            from bigfish.apps.schools.views import push_info_to_wx
            push_info_to_wx(user_list, task_obj.question_data.__len__())
        # 题目不同创建作业
        else:
            for user_id in user_list:
                try:
                    question_dict[user_id]
                except:
                    question_dict[user_id] = ''
                data_dict = {'task_push_record': tpr, 'user_id': user_id, 'question_data': question_dict[user_id]}
                sql = ReceiveRecord(**data_dict)
                sql_list.append(sql)
            ReceiveRecord.objects.bulk_create(sql_list)
            # 记录推送次数
            task_obj.push_num = task_obj.push_num + 1
            task_obj.save()
            push_individuation_homework(user_list, tpr.id)
    return Response(rsp_msg_200({'user_list': user_list}), status=status.HTTP_200_OK)


def push_individuation_homework(user_list, taskpushrecord_id):
    """
        推送信息到微信
        :param user_list:
        :param nums:
        :return:
    """
    url = WEHOST + "/api/bfwechat/template_msg_record/send_template/"
    for ul in user_list:
        wx_ul = WxUserRelationship.objects.filter(student=ul)
        if wx_ul.count() == 0:
            continue

        # 个性化作业获取用户题目数量
        try:
            ReceiveRecord = ReceiveRecord.objects.get(task_push_record=taskpushrecord_id, user_id=ul)
        except:
            return Response(rsp_msg_400('用户没有这条作业记录'), status=status.HTTP_200_OK)
        if ReceiveRecord.question_data:
            nums = len(ReceiveRecord.question_data.split(','))
        else:
            continue
        for wxu in wx_ul:
            nick_name = wxu.wx_user.nickname
            student_name = wxu.student.profile.realname
            openid = wxu.wx_user.openid
            first = "Hi~尊敬的{}用户您好！今日（{}）作业已发布请各位家长及时监督学生完成作业。". \
                format(nick_name, wxu.student.profile.realname)
            content = "本次练习总计{}道题目。".format(nums)
            data_temp = {
                "openid": openid,
                "template": {
                    "template_id": "BaEPWB9SVLUYueXexR0ur-ct6IKkP6GIg4WWTvVPRRM",
                    "url": "",
                    "mini_program":
                        {
                            "appid": "wxe083dfd04f3ba126",
                            "pagepath": ""
                        },
                    "data":
                        {
                            "first": {
                                "value": first
                            },
                            "name": {
                                "value": student_name
                            },
                            "subject": {
                                "value": "英语"
                            },
                            "content": {
                                "value": content
                            },
                            "remark": {
                                "value": "点击查看详情"
                            }
                        }
                }
            }
            from bigfish.base.response import fmt_url_post
            fmt_url_post(url, **data_temp)
    return


def create_wrongtopic(request, topic_data, question_id):
    """错题本数据存储"""
    user = request.user
    answer_detail = request.data.get('answer_detail', "")
    # 作业提交数据没有传data_source数据，来源默认为3
    data_source = request.data.get('data_source', 3)
    # 添加来源
    topic_data.update({'data_source': data_source})
    try:
        homework_time = topic_data.pop('homework_time')
    except:
        homework_time = ''
    # 错误场景
    """
        1.任务下展示格式：任务名称（布置的任务XX）- 单元 - lesson - 活动名
        2.自主学习展示格式：自主学习 - 单元 - lesson - 活动名
        3.作业下展示格式：2018-08-11 周三 布置的作业
        4.错题本下展示格式：自主学习-错题本-综合复习

    """
    if data_source == 6:
        scene = '自主学习-{}-{}-{}'.format(topic_data['unit_name'], topic_data['lesson_name'],
                                       topic_data['name_type'])
        topic_data.update({'scene': scene})
    elif data_source == 1:
        scene = '自主学习-错题本-综合复习'
        topic_data.update({'scene': scene})
    elif topic_data == 3:
        scene = '{}-{}-布置的作业'.format(topic_data[homework_time].strftime('%Y-%m-%d'), topic_data[homework_time].weekday() + 1)
        topic_data.update({'scene': scene})
    elif data_source == 7:
        scene = '{}-{}-{}-{}'.format(topic_data['task_name'], topic_data['unit_name'], topic_data['lesson_name'],
                                     topic_data['activity_name'])
        topic_data.update({'scene': scene})
    elif data_source == 2:
        scene = '{}-{}-{}-{}'.format(topic_data['task_name'], topic_data['unit_name'], topic_data['lesson_name'],
                                     topic_data['name_type'])
        topic_data.update({'scene': scene})

    # try:
    #     question_queryset = QuestionKPRelationship.objects.get(question_id=question_id)
    # except:
    #     return Response(rsp_msg_400(msg='传入的题目id有误'), status=status.HTTP_200_OK)
    # else:
    #     # QuestionKPRelationship.objects.get(question=question)
    #     knowledge_queryset = question.knowledge_point.all().order_by('order', 'seconds')
    # 根据题查找知识点
    knowledge_queryset = QuestionKPRelationship.objects.filter(question_id=question_id).order_by('order', 'seconds')

    try:
        topic_data.pop('name_type')
    except:
        pass
    if knowledge_queryset.exists():
        for index, knowledge in enumerate(knowledge_queryset):
            # 判断每个空的对错
            topic_dict = {}
            knowledge_data = {}
            topic_dict.update(topic_data)
            answer = answer_detail[knowledge.order - 1]['answer']
            if len(answer) == 0:
                is_right = answer_detail[knowledge.order - 1]['is_right']
            else:
                # 消消乐空的提交顺序不确定 获取content对应到指定的空
                question = Question.objects.get(id=question_id)
                question_content_list = question.content.split('&')
                spell_name = question_content_list[knowledge.order - 1].split('|')[0]
                for detail in answer_detail:
                    if detail['spell'] == spell_name:
                        is_right = detail['answer'][0]['is_right']
                        break
            try:
                wrongtopic = WrongTopic.objects.get(kp_coding=knowledge.knowledge_point.coding, user_id=user.id)
            except:
                # 创建错题本记录
                if is_right:
                    master_level = 6
                else:
                    master_level = 1
                    # 第一次做错
                    knowledge_data.update({'ever_wrong': True})
                knowledge_data.update({'kp_name': knowledge.knowledge_point.name, 'kp_coding': knowledge.knowledge_point.coding,
                                  'master_level': master_level})
                topic_dict.update(knowledge_data)
                wrongtopic = WrongTopic.objects.create(**topic_dict)
                topic_dict.update({'wrong_topic': wrongtopic})
                try:
                    topic_dict.pop('ever_wrong')
                except:
                    WrongTopicHis.objects.create(**topic_dict)
                else:
                    WrongTopicHis.objects.create(**topic_dict)
            else:
                # 更新错题本知识点数据
                knowledge_data = {'kp_name': knowledge.knowledge_point.name, 'kp_coding': knowledge.knowledge_point.coding}
                knowledge_data.update(topic_data)
                if is_right == 0 and 1 < wrongtopic.master_level <= 6:
                    # 错误就更新场景
                    knowledge_data.update({'scene': topic_dict['scene']})
                    if wrongtopic.ever_wrong:
                        wrongtopic.master_level -= 1
                        # 等级下降更新控制弹出字段
                        knowledge_data.update({'is_pop': False})
                    else:
                        wrongtopic.master_level = 1
                        knowledge_data.update({'ever_wrong': True})
                elif is_right == 0 and wrongtopic.master_level == 1:
                    wrongtopic.master_level = 1
                    # 错误就更新场景
                    knowledge_data.update({'scene': topic_dict['scene']})
                elif is_right == 1 and 1 <= wrongtopic.master_level < 6:
                    wrongtopic.master_level += 1
                    # 不是自主复习达到6级 设置弹出该知识点
                    if data_source != 1 and wrongtopic.master_level == 6:
                        knowledge_data.update({'is_pop': True})
                elif is_right == 1 and wrongtopic.master_level == 6:
                    wrongtopic.master_level = 6
                knowledge_data.update({'master_level': wrongtopic.master_level})
                WrongTopic.objects.filter(kp_coding=knowledge.knowledge_point.coding, user_id=user.id).update(**knowledge_data)
                topic_dict.update(knowledge_data)
                topic_dict.update({'wrong_topic': wrongtopic})

                try:
                    topic_dict.pop('ever_wrong')
                except:
                    WrongTopicHis.objects.create(**topic_dict)
                else:
                    WrongTopicHis.objects.create(**topic_dict)
    else:
        return Response(rsp_msg_400('该题目没有对应的知识点'), status=status)






