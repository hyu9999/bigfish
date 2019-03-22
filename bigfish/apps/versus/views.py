import datetime
import logging
import random

from django.contrib.auth.models import User
from django.db.models import Avg, Q, Count
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from bigfish.apps.schools.models import School, Klass
from bigfish.apps.users.models import BigfishUser
from bigfish.apps.versus.models import VersusDetail, Versus
from bigfish.apps.versus.serializers import VersusDetailSerializer, VersusSerializer
from bigfish.base import viewsets, status
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400
from bigfish.utils.functions import get_range_time

logger = logging.getLogger("django")


class VersusViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a versus instance.
    list:
        Return all versus, ordered by most recently joined.
    create:
        Create a new versus.
    delete:
        Remove an existing versus.
    partial_update:
        Update one or more fields on an existing versus.
    update:
        Update a versus.
    """
    queryset = Versus.objects.all()
    serializer_class = VersusSerializer

    @detail_route()
    def get_vs_detail(self, request, *args, **kwargs):
        """
        get versus detail by versus id

        :method: GET\n
        :param:\n
            pk
        :return:\n
            {
              "result": "success",
              "code": 200,
              "detail": {
                "id": 1,
                "competitor_type": 1, # 0:AI 1:用户
                "complete_type": 0, # 0:未完成 1:正常退出 2:完成
                "pk_type": 0, # 0:任务对战 1:自由对战
                "task": "",
                "start_time": "2017-09-29T13:59:00",
                "end_time": "2017-10-09T13:57:00",
                "pk_user": 1,
                "head_icon": null,
                "pet_name": "kkk",
                "speed": 2,
                "score": 100,
                "real_score": 80,
                "big_fishery": 90,
                "pk_result": 1, # 0:负 1:胜
                "right_times": 20,
                "wrong_times": 10,
                "total_times": 30,
                "user_ai": "",
                "ai_icon": null,
                "ai_icon_frame": null,
                "pet_name_ai": "",
                "speed_ai": null,
                "score_ai": null,
                "real_score_ai": null,
                "big_fishery_ai": null,
                "pk_result_ai": 0, # 0:负 1:胜
                "right_times_ai": null,
                "wrong_times_ai": null,
                "total_times_ai": null,
                "competitor": {
                  "id": 2,
                  "competitor_type": 1,
                  "complete_type": 0,
                  "pk_type": 0,
                  "task": "",
                  "start_time": "2017-09-29T13:59:00",
                  "end_time": "2017-10-04T13:58:00",
                  "pk_user": 5,
                  "head_icon": null,
                  "pet_name": "ssss",
                  "speed": 3,
                  "score": 90,
                  "real_score": 80,
                  "big_fishery": 60,
                  "pk_result": 0,
                  "right_times": 20,
                  "wrong_times": 10,
                  "total_times": 30,
                  "user_ai": "",
                  "ai_icon": null,
                  "ai_icon_frame": null,
                  "pet_name_ai": "",
                  "speed_ai": null,
                  "score_ai": null,
                  "real_score_ai": null,
                  "big_fishery_ai": null,
                  "pk_result_ai": 0,
                  "right_times_ai": null,
                  "wrong_times_ai": null,
                  "total_times_ai": null,
                  "competitor": 1
                },
                "versus_details": {
                  "listen_to_picture": [
                    [
                      {
                        "id": 4,
                        "order": 1,
                        "user_type": 0, # 0:organizer 1:competitor 2:ai
                        "word": 27700,
                        "question_type": "listen_to_picture",
                        "result": 0, # 0:错 1:对 2:未答
                        "word_spell": "cat"
                      },
                      {
                        "id": 2,
                        "order": 1,
                        "user_type": 1,
                        "word": 27700,
                        "question_type": "listen_to_picture",
                        "result": 0,
                        "word_spell": "cat"
                      }
                    ],
                    [
                      {
                        "id": 7,
                        "order": 4,
                        "user_type": 0,
                        "word": 27716,
                        "question_type": "listen_to_picture",
                        "result": 0,
                        "word_spell": "eraser"
                      }
                    ]
                  ],
                  "look_at_word": [
                    [
                      {
                        "id": 5,
                        "order": 2,
                        "user_type": 0,
                        "word": 27705,
                        "question_type": "look_at_word",
                        "result": 0,
                        "word_spell": "bear"
                      },
                      {
                        "id": 13,
                        "order": 2,
                        "user_type": 1,
                        "word": 27705,
                        "question_type": "look_at_word",
                        "result": 1,
                        "word_spell": "bear"
                      }
                    ]
                  ],
                  "english_translation": [
                    [
                      {
                        "id": 6,
                        "order": 3,
                        "user_type": 0,
                        "word": 27717,
                        "question_type": "english_translation",
                        "result": 0,
                        "word_spell": "sharpener"
                      },
                      {
                        "id": 14,
                        "order": 3,
                        "user_type": 1,
                        "word": 27717,
                        "question_type": "english_translation",
                        "result": 1,
                        "word_spell": "sharpener"
                      }
                    ]
                  ]
                }
              }
            }
        """
        pk = kwargs.get('pk', None)
        versus = Versus.objects.get(id=pk)
        versus_serializer = VersusSerializer(versus)
        competitor = VersusSerializer(versus.competitor).data
        competitor.pop('versus_details', None)
        versus_data = versus_serializer.data
        versus_data['competitor'] = competitor
        data = {"result": "success", "code": 200, "detail": versus_data}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def get_combat_record(self, request):
        user = request.user
        day_record = {}
        history_record = {}
        now_time = datetime.datetime.now()
        day_time = datetime.date(now_time.year, now_time.month, now_time.day)
        day_record['win'] = Versus.objects.filter(pk_user=user, pk_result=1, end_time__date=day_time,
                                                  complete_type=2).count()
        day_record['lost'] = Versus.objects.filter(pk_user=user, pk_result=0, end_time__date=day_time,
                                                   complete_type=2).count()
        history_record['win'] = Versus.objects.filter(pk_user=user, pk_result=1, complete_type=2).count()
        history_record['lost'] = Versus.objects.filter(pk_user=user, pk_result=0, complete_type=2).count()
        data = {"detail": {"day_record": day_record, "history_record": history_record}, "code": 200}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def get_versus_record(self, request):
        user = request.user
        day_list = []
        history_list = []
        now_time = datetime.datetime.now()
        day_time = datetime.date(now_time.year, now_time.month, now_time.day)
        versus_day = Versus.objects.filter(pk_user=user, end_time__date=day_time,
                                           complete_type=2).order_by('-end_time')
        for versus in versus_day:
            day_versus = {'id': versus.id, 'own_name': user.profile.nickname, 'own_icon': user.profile.icon}
            user_type = versus.competitor_type
            if user_type == 0:
                day_versus['other_name'] = versus.user_ai
                day_versus['other_icon'] = versus.ai_icon
            elif user_type == 1:
                day_versus['other_name'] = versus.competitor.pk_user.profile.nickname
                day_versus['other_icon'] = versus.competitor.pk_user.profile.icon
            day_versus['versus_time'] = versus.start_time
            day_versus['owen_win'] = versus.pk_result
            day_list.append(day_versus)
        versus_history = Versus.objects.filter(pk_user=user, complete_type=2).order_by('-end_time')
        for versus in versus_history:
            history_versus = {'id': versus.id, 'own_name': user.profile.nickname, 'own_icon': user.profile.icon}
            user_type = versus.competitor_type
            if user_type == 0:
                history_versus['other_name'] = versus.user_ai
                history_versus['other_icon'] = versus.ai_icon
            elif user_type == 1:
                history_versus['other_name'] = versus.competitor.pk_user.profile.nickname
                history_versus['other_icon'] = versus.competitor.pk_user.profile.icon
            history_versus['versus_time'] = versus.start_time
            history_versus['owen_win'] = versus.pk_result
            history_list.append(history_versus)
        data = {"detail": {"day_list": day_list, "history_list": history_list}, "code": 200}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)


class VersusDetailViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a versus detail instance.
    list:
        Return all versus detail, ordered by most recently joined.
    create:
        Create a new versus detail.
    delete:
        Remove an existing versus detail.
    partial_update:
        Update one or more fields on an existing versus detail.
    update:
        Update a versus detail.
    """
    queryset = VersusDetail.objects.all().order_by('question_type', 'order')
    serializer_class = VersusDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(rsp_msg_200(serializer.data), status=status.HTTP_200_OK, headers=headers)

    @list_route(methods=['POST'])
    def random_create(self, request):
        """
        create a robot

        :method: POST\n
        :param:\n
            {"user":1}
        :return:\n
            {
              "result": "success",
              "code": 200,
              "detail": {
                "name": "gyh434",
                "icon": "/media/asd.jpg",
                "pic_frame": "",
                "pet": {
                  "id": 3,
                  "name": "3",
                  "shield": 3,
                  "attack": 3,
                  "crit": 3,
                  "icon": "/media/3.jpg",
                  "price": 3,
                  "freehero": "3",
                  "order": 3
                },
                "user_pet": {
                  "id": 3,
                  "name": "3",
                  "shield": 3,
                  "attack": 3,
                  "crit": 3,
                  "icon": "/media/3.jpg",
                  "price": 3,
                  "freehero": "3",
                  "order": 3
                },
                "speed": 7.3,
                "correct_rate": 74
              }
            }
        """
        user_id = request.data.get("user", None)
        try:
            user = User.objects.get(id=user_id)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400("用户不存在"), status=status.HTTP_200_OK)
        # ret_data = {
        #     'name': generate_robot_name(user),
        #     # 'icon': generate_icon(),
        #     'pic_frame': generate_pic_frame()
        # }
        # pet_info = generate_pet(user)
        # if pet_info:
        #     ret_data.update(pet_info)
        # else:
        #     return Response(rsp_msg_400("未查询到用户宠物信息"), status=status.HTTP_200_OK)
        # ret_data.update(generate_ai_info(user))
        # data = {"result": "success", "code": 200, "detail": ret_data}
        # return Response(rsp_msg_200(msg=data), status=status.HTTP_200_OK)

    @list_route()
    def versus_report(self, request):
        """
        对战报告（教师端）

        :method: GET\n
        :param:\n
            klass=1
            type=1(1.今天；2.本周；3.上周)
            start_date=2017-09-29
            end_date=2017-09-29
        :return:\n
            {
                "result": "success",
                "code": 200,
                "detail": {
                    "word": [
                        {
                            "word__spell": "cat",
                            "num": 3
                        },
                        {
                            "word__spell": "eraser",
                            "num": 2
                        },
                        {
                            "word__spell": "bear",
                            "num": 1
                        },
                        {
                            "word__spell": "orange",
                            "num": 1
                        },
                        {
                            "word__spell": "pencil",
                            "num": 1
                        },
                        {
                            "word__spell": "sharpener",
                            "num": 1
                        }
                    ],
                    "module": [
                        {
                            "question_type": "listen_to_picture",
                            "num": 5
                        },
                        {
                            "question_type": "english_translation",
                            "num": 2
                        },
                        {
                            "question_type": "look_at_word",
                            "num": 2
                        }
                    ]
                }
            }
        """

        klass = request.GET.get('klass', None)
        if not klass:
            return Response(rsp_msg_400("请传入班级id"), status=status.HTTP_200_OK)
        start_date, end_date = get_search_date(request)
        students = BigfishUser.objects.filter(default_cid=klass, identity='学生').values_list('user', flat=True)
        all_result = VersusDetail.objects.filter(versus__end_time__date__range=(start_date, end_date),
                                                 user_type__in=[0, 1], versus__pk_user__in=students, result=0)
        wrong_word_result = all_result.values('word__spell').annotate(num=Count('word')).order_by('-num')
        wrong_type_result = all_result.values('question_type').annotate(
            num=Count('question_type')).order_by('question_type')
        data = {'word': wrong_word_result, 'module': wrong_type_result}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)


def get_search_date(request):
    type_val = request.GET.get('type', None)
    current_date = datetime.datetime.now().date()
    if type_val:
        if type_val == '1':  # 今天
            start_date, end_date = current_date, current_date
        elif type_val == '2':  # 本周
            start_date, end_date = get_range_time(current_date, from_val=1, to_val=7)
        elif type_val == '3':  # 上周
            start_date, end_date = get_range_time(current_date, from_val=-6, to_val=0)
        else:
            raise ValidationError(rsp_msg_400("传入类型错误"))
    else:
        start_date = request.GET.get('start_date', current_date)
        end_date = request.GET.get('end_date', current_date)
    return start_date, end_date


def generate_robot_name(user):
    try:
        user_school = Klass.objects.get(id=user.profile.default_cid).school
    except Exception as e:
        logger.debug(e)
        raise ValidationError(rsp_msg_400("未查询到该用户所在学校"))
    normal_school = School.objects.filter(~Q(id=user_school.id), is_normal=True)
    default_cid_list = [str(x) for x in Klass.objects.filter(school__in=normal_school).values_list('id', flat=True)]
    try:
        random_nickname = BigfishUser.objects.filter(identity="学生", default_cid__in=default_cid_list,
                                                     nickname__isnull=False).order_by('?')[:1][0].nickname
    except Exception as e:
        logger.debug(e)
        raise ValidationError(rsp_msg_400("未查询到随机昵称"))
    return random_nickname


# def generate_pet(user):
#     try:
#         user_pet = Userhero.objects.get(user=user, is_active=True).hero
#     except Exception as e:
#         logger.debug(e)
#         return {}
#     else:
#         icon_order = user_pet.order
#     multiple = ceil(icon_order / 3)
#     order_list = []
#     for x in range(0, 3):
#         tmp = multiple * 3 - x
#         order_list.append(tmp)
#     pet = Wordhero.objects.filter(order__in=order_list).order_by('?')[:1][0]
#     return {'pet': WordheroSerializer(pet).data, 'user_pet': WordheroSerializer(user_pet).data}


# def generate_icon():
#     try:
#         icon = UserHeadicon.objects.all().order_by('?')[:1][0].icon.url
#     except Exception as e:
#         logger.debug(e)
#         return None
#     return icon


def generate_pic_frame():
    return ""


def generate_ai_info(user):
    speed = get_user_speed(user)
    correct_rate = get_correct_rate(user)
    if correct_rate in range(0, 30):
        robot_correct_rate = correct_rate + random.randint(-10, -1)
        robot_speed = speed + random.randint(10, 30)
    elif correct_rate in range(30, 60):
        robot_correct_rate = correct_rate + random.randint(-7, 3)
        robot_speed = speed + random.randint(-10, 15) / 10
    elif correct_rate in range(60, 80):
        robot_correct_rate = correct_rate + random.randint(-3, 7)
        robot_speed = speed + random.randint(-20, 10) / 10
    elif correct_rate in range(80, 101):
        robot_correct_rate = correct_rate + random.randint(1, 10)
        robot_speed = speed + random.randint(-20, 10) / 10
    else:
        robot_correct_rate = correct_rate
        robot_speed = speed
    if robot_correct_rate >= 100:
        robot_correct_rate = 100
    if robot_correct_rate <= 5:
        robot_correct_rate = 5
    if robot_speed >= 8:
        robot_speed = 8
    if robot_speed <= 1.5:
        robot_speed = 1.5

    ret_data = {"speed": round(robot_speed, 1), "correct_rate": round(robot_correct_rate, 0)}
    return ret_data


def get_user_speed(user):
    speed = Versus.objects.filter(pk_user=user).aggregate(Avg("speed_ai"))
    if speed['speed_ai__avg']:
        speed = speed['speed_ai__avg']
        return speed
    else:
        return 8


def get_correct_rate(user):
    try:
        correct_rate = Versus.objects.filter(pk_user=user).aggregate(
            correct_rate=Avg("right_times") / Avg("total_times") * 100)
    except Exception as e:
        logger.debug(e)
        return 5
    else:
        if correct_rate['correct_rate']:
            correct_rate = round(correct_rate['correct_rate'])
            return correct_rate
        else:
            return 5
