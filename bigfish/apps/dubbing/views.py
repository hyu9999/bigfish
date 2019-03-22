import json
from collections import OrderedDict
from datetime import timedelta, datetime

import xlrd
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import Count
from rest_framework.decorators import list_route, api_view, permission_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from bigfish.apps.attention.models import AttentionCircle
from bigfish.apps.dubbing.models import DubbingSRC, UserDubbing, DubbingZan, DubbingRead, \
    DubbingCategory, DubbingMain, DubbingClick, Competition, SubCompetition, CompetitionRank, RewardConfig
from bigfish.apps.dubbing.serializers import DubbingSRCSerializer, UserDubbingSerializer, DubbingZanSerializer, \
    DubbingReadSerializer, DubbingCategorySerializer, DubbingMainSerializer, \
    DubbingClickSerializer, CompetitionSerializer, SubCompetitionSerializer, CompetitionRankSerializer, \
    RewardConfigSerializer, UDMinSerializer
from bigfish.apps.dubbing.tools import competition_settlement
from bigfish.apps.schools.models import School, Klass
from bigfish.apps.textbooks.models import Activity
from bigfish.apps.users.models import BigfishUser
from bigfish.apps.users.serializers import MinUserSerializer
from bigfish.base import viewsets, status
from bigfish.base.permissions import Everyone
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400
from bigfish.utils.db import dict_fetchall


class DubbingMainViewSet(viewsets.ModelViewSet):
    """
    主分类
    """
    queryset = DubbingMain.objects.all()
    serializer_class = DubbingMainSerializer
    parser_classes = (JSONParser, MultiPartParser)
    filter_fields = ('id', 'is_active', 'is_default')

    @list_route(methods=['GET'])
    def get_homepage_data(self, request):
        user = request.user
        results = []
        d_list = DubbingMain.objects.filter(is_default=False)
        for m in d_list:
            d_src = DubbingSRC.objects.filter(dubbing_category__dubbing_main=m, is_active=True, is_lesson=False). \
                order_by('order')
            for d in d_src:
                ud_list = UserDubbing.objects.filter(dubbingsrc=d, user=user)
                t_data = DubbingSRCSerializer(d).data
                t_data.pop('score_rule')
                if ud_list:
                    t_data['is_done'] = True
                else:
                    t_data['is_done'] = False
                results.append(t_data)
        return Response(rsp_msg_200(results), status=status.HTTP_200_OK)


def get_grouping_data(user, id):
    results = []
    grouping_order = DubbingSRC.objects.filter(dubbing_category=id, is_lesson=False, is_active=True).order_by(
        'grouping')
    l_group = grouping_order.values('grouping').distinct()
    for group in l_group:
        src_l = DubbingSRC.objects.filter(grouping=group['grouping'], is_lesson=False, is_active=True).order_by('order')
        temp = []
        for src in src_l:
            data = DubbingSRCSerializer(src).data
            data.pop('score_rule')
            ud_list = UserDubbing.objects.filter(user=user, dubbingsrc=src)
            if ud_list:
                data['is_done'] = True
            else:
                data['is_done'] = False
            temp.append(data)
        results.append(temp)
    return results


class DubbingCategoryViewSet(viewsets.ModelViewSet):
    """
    二级分类
    """
    queryset = DubbingCategory.objects.all()
    serializer_class = DubbingCategorySerializer
    parser_classes = (JSONParser, MultiPartParser)
    filter_fields = ('id', 'is_active', 'is_default')

    @list_route(methods=['GET'])
    def get_category_data(self, request):
        results = []
        t_data = []
        user = request.user
        c_lower = request.GET.get('lowerid')
        if c_lower:
            results = get_grouping_data(user, int(c_lower))
        else:
            c_top = request.GET.get('topid')
            t_list = DubbingCategory.objects.filter(dubbing_main=c_top).order_by('order')
            t_data = DubbingCategorySerializer(t_list, many=True).data
            if t_data:
                f_id = t_data[0]['id']
                results = get_grouping_data(user, f_id)
            else:
                results = []
        return Response({"data": results, "detail": t_data, "message": "success", "code": 200},
                        status=status.HTTP_200_OK)


class DubbingSRCViewSet(viewsets.ModelViewSet):
    """
    配音创建修改删除
    """
    queryset = DubbingSRC.objects.all()
    serializer_class = DubbingSRCSerializer
    parser_classes = (JSONParser, MultiPartParser)
    filter_fields = ('id', 'is_lesson', 'dubbing_category')

    @list_route(methods=["post"])
    def import_dubbingsrc(self, request):
        """
        导入趣配音资源数据 \n
        \t导入表头：/video视频/audio音频/image图片/dialogue/dubbing_category\n
        \t参数：  {"file_url":"/media/xxx.xlsx"}
        """

        file_url = request.data.get("file_url", "")
        file_path = settings.MEDIA_ROOT.replace("media", "") + file_url
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        errors = []
        with transaction.atomic():
            for index in range(1, sheet.nrows):
                values = [str(item.value) for item in sheet.row(index)]
                if not (values[0] and values[2] and values[3] and values[4] and values[5] and values[6] and values[7]):
                    errors.append({"line": index + 1, "message": "关键信息不能为空"})
                    continue
                video = values[0]
                audio = values[1]
                image = values[2]
                try:
                    dialogue = json.loads(values[3])
                except Exception as e:
                    print(e)
                    dialogue = values[3]
                if values[4].endswith(".0"):
                    dubbing_category = values[4][:-2]
                else:
                    dubbing_category = values[4]
                try:
                    category_obj = DubbingCategory.objects.get(id=dubbing_category)
                except:
                    continue
                try:
                    score_rule = json.loads(values[5])
                except:
                    score_rule = values[5]
                click_num = 0
                is_lesson = False
                is_active = True
                is_banner = False
                grouping = values[6]
                description = values[7]
                if values[8].endswith(".0"):
                    order = values[8][:-2]
                else:
                    order = values[8]
                stop_image = values[9]
                data = {
                    "video": video,
                    "audio": audio,
                    "image": image,
                    "dialogue": dialogue,
                    "dubbing_category": category_obj,
                    "score_rule": score_rule,
                    "click_num": click_num,
                    "is_lesson": is_lesson,
                    "is_active": is_active,
                    "is_banner": is_banner,
                    "grouping": grouping,
                    "description": description,
                    "order": int(order),
                    "stop_image": stop_image
                }
                try:
                    exist_word = DubbingSRC.objects.get(description=description)
                    # exist_word.audio = audio
                    exist_word.order = order
                    exist_word.stop_image = stop_image
                    exist_word.save()
                except Exception as e:
                    try:
                        DubbingSRC.objects.create(**data)
                    except  Exception as e:
                        print(e)
                        return Response(data=dict(message='error', errors=errors, code=0))
        if errors:
            if (sheet.nrows - 1) == len(errors):
                return Response(data=dict(message='error', errors=errors, code=0))
            return Response(data=dict(message='part success', errors=errors, code=0))
        else:
            return Response(data=dict(message='success', errors=errors, code=0))


class UserDubbingViewSet(viewsets.ModelViewSet):
    """
    作品创建修改删除
    """
    serializer_class = UserDubbingSerializer
    queryset = UserDubbing.objects.all()
    parser_classes = (JSONParser, MultiPartParser)
    filter_fields = ('id', 'user', 'is_active', 'dubbingsrc_id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        obj = UserDubbing.objects.get(id=serializer.data['id'], is_active=True)
        headers = self.get_success_headers(serializer.data)
        if obj:
            at_list = AttentionCircle.objects.filter(user=obj.user.id)
            for at in at_list:
                user_obj = User.objects.get(id=at.fans)
                data = {'user': user_obj, 'userdubbing': obj, 'is_read': False}
                DubbingRead.objects.create(**data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['GET'])
    def user_list(self, request):
        """
        xx视频配音用户列表(配音作品为最新配音的一次)

        :param request: \n
            dubbingsrc_id=1[&page_size=10][&page=1]
        :return: \n
            {
                "data": [
                    {
                        "create_time": "2018-05-30T10:11:35.062684",
                        "zan_num": 0,
                        "description": "Look at me!",
                        "user_id": 16,
                        "video_url": "",
                        "icon": "1",
                        "realname": "用户00000001",
                        "userdubbing_id": 98
                    },
                    {
                        "create_time": "2018-05-30T17:07:10.937967",
                        "zan_num": 0,
                        "description": "Look at me!",
                        "user_id": 17,
                        "video_url": "",
                        "icon": "1",
                        "realname": "北京学生06",
                        "userdubbing_id": 104
                    }
                ],
                "message": "success",
                "code": 200
            }
        """
        dubbingsrc_id = request.query_params.get("dubbingsrc_id", None)
        if not dubbingsrc_id:
            raise BFValidationError("传参错误！")
        sql_str = """
            SELECT DISTINCT ON ( A.user_id ) 
                C.description as description,
                b.icon as icon,
                b.realname as realname,
                a.zan_num as zan_num,
                A.ID as userdubbing_id,
                A.video_url as video_url,
                A.user_id as user_id,
                A.create_time as create_time
            FROM
                dubbing_userdubbing A
                 JOIN users_bigfishuser b ON A.user_id = b.id
                 JOIN dubbing_dubbingsrc C ON A.dubbingsrc_id = C.ID
            WHERE
                A.dubbingsrc_id = {}
            ORDER BY
                A.user_id ASC,
                A.create_time DESC;

        """.format(dubbingsrc_id)
        with connection.cursor() as cursor:  # with语句相当与cursor= connection.cursor() 和 cursor.close(),简化了语句
            cursor.execute(sql_str)
            row = dict_fetchall(cursor)

        return Response(rsp_msg_200(row), status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def min_list(self, request, *args, **kwargs):
        """
        1.获取xx用户配音作品列表\n
            user=1[&page_size=10][&page=1]
        2.xx配音作品点赞排行\n
            dubbingsrc=1[&page_size=10][&page=1]

        :param request: \n
        :param args: \n
        :param kwargs: \n
        :return: \n
            {
                "message": "success",
                "code": 200,
                "data": {
                    "count": 1,
                    "next": null,
                    "previous": null,
                    "results": [
                        {
                            "id": 1,
                            "video": null,
                            "video_url": "",
                            "user": 2,
                            "user_icon": null,
                            "zan_num": 0,
                            "is_competition": false,
                            "is_zan": false,
                            "src_image": "/media/dubbing/base/LookAtMe_01.png",
                            "create_time": "2019-01-08T11:42:32.624000",
                            "description": "test"
                        }
                    ]
                }
            }
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('-zan_num', 'create_time')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UDMinSerializer(page, many=True)
            ret_data = serializer.data
            for item in ret_data:
                try:
                    DubbingZan.objects.get(user=request.user, userdubbing_id= item.get("id"))
                except Exception as e:
                    item["is_zan"] = False
                else:
                    item["is_zan"] = True
            return self.get_paginated_response(serializer.data)

        serializer = UDMinSerializer(queryset, many=True)
        ret_data = serializer.data
        for item in ret_data:
            try:
                DubbingZan.objects.get(user=request.user, userdubbing_id=item.get("id"))
            except Exception as e:
                item["is_zan"] = False
            else:
                item["is_zan"] = True
        return Response(rsp_msg_200(serializer.data))

    @list_route(methods=['GET'])
    def get_userdubbing_list(self, request):
        """
        用户当期作品以及其他配音作品
        """
        user = request.GET.get('user')
        results = {}
        if not user:
            return Response({"results": {}, "message": "user是必传字段！", "code": 400},
                            status=status.HTTP_200_OK)
        userdubbing = request.GET.get('userdubbing')
        if not userdubbing:
            return Response({"results": {}, "message": "userdubbing是必传字段！", "code": 400},
                            status=status.HTTP_200_OK)
        ud_list = UserDubbing.objects.filter(user=user, is_active=True).exclude(id=userdubbing).order_by(
            '-create_time')[:2]
        list_data = UserDubbingSerializer(ud_list, many=True).data
        try:
            user_obj = UserDubbing.objects.get(id=userdubbing, is_active=True)
        except Exception as e:
            return Response({"results": {}, "message": "查询不到配音作品！", "code": 400}, status=status.HTTP_200_OK)
        user_data = UserDubbingSerializer(user_obj).data
        user_data['dialogue'] = user_obj.dubbingsrc.dialogue
        user_data['src_video'] = user_obj.dubbingsrc.video.url
        user_data['src_audio'] = user_obj.dubbingsrc.audio.url
        user_data['src_image'] = user_obj.dubbingsrc.image.url
        user_data['is_lesson'] = user_obj.dubbingsrc.is_lesson
        results['data'] = list_data
        results['detail'] = user_data
        return Response(rsp_msg_200(results), status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def get_dubbingsrc_data(self, request):
        activity = request.GET.get('activity', "")
        try:
            act = Activity.objects.control().get(id=activity)
        except:
            return Response({"data": [], "message": "未查询到相应的活动信息，请检查传入参数", "code": 400},
                            status=status.HTTP_200_OK)
        data = act.question_data
        if data:
            id_list = data['dubbingsrc']
            dubbing_list = DubbingSRC.objects.filter(id__in=id_list)
        else:
            return Response({"data": [], "message": "此活动配置为空，请检查配置内容", "code": 400},
                            status=status.HTTP_200_OK)
        results = DubbingSRCSerializer(dubbing_list, many=True).data
        return Response(rsp_msg_200(results), status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def ud_batch_update(self, request):
        """
        batch update tasks

        :param request:\n
            method:post
            params: {
                        "id_list":[1,2,3],
                        "modify_data":{
                            "key1":"value1",
                            "key2":"value2"
                        }
                    }
        :return:
        """
        id_list = request.data.get("id_list", None)
        modify_data = request.data.get("modify_data", None)
        ud_querysets = UserDubbing.objects.filter(id__in=id_list, is_active=True)
        try:
            success_num = ud_querysets.update(**modify_data)
        except Exception as e:
            return Response(rsp_msg_400(str(e)), status.HTTP_200_OK)
        return Response(rsp_msg_200("{} update success".format(success_num)), status.HTTP_200_OK)


class DubbingClickViewSet(viewsets.ModelViewSet):
    queryset = DubbingClick.objects.all()
    serializer_class = DubbingClickSerializer
    filter_fields = ('id', 'dubbingsrc__id')


class DubbingZanViewSet(viewsets.ModelViewSet):
    serializer_class = DubbingZanSerializer
    queryset = DubbingZan.objects.all()
    parser_classes = (JSONParser, MultiPartParser)
    filter_fields = ('id', 'user',)

    @list_route(methods=['POST'])
    def user_dubbing_zan(self, request):
        """
        用户趣配音作品点赞（点过赞24h内不允许再点赞）

        :param request:\n
           {"user_id":17,"userdubbing_id":100}
        :return:\n
            {
              "data": {},
              "code": "200",
              "message": "点赞成功"
            }
            or
            {
              "data": {},
              "code": "400",
              "message": "已点过赞"
            }
        """
        with transaction.atomic():
            try:
                obj, flag = DubbingZan.objects.get_or_create(**request.data)
            except Exception as e:
                raise BFValidationError("参数错误")
            # 已点过赞
            if not flag:
                # 如果点过赞，24h内不允许点赞
                if obj.create_time + timedelta(days=1) > datetime.now():
                    return Response(rsp_msg_400(msg="已点过赞"), status=status.HTTP_200_OK)
            # 点赞数增加
            obj.zan_num = (obj.zan_num or 0) + 1
            obj.save()
            # 更新用户配音作品中的点赞数
            try:
                ud_obj = UserDubbing.objects.get(id=obj.userdubbing_id)
            except Exception as e:
                raise BFValidationError("更新点赞数失败")
            else:
                ud_obj.zan_num = (ud_obj.zan_num or 0) + 1
                ud_obj.save()
        headers = self.get_success_headers(self.get_serializer(obj).data)
        return Response(rsp_msg_200(msg="点赞成功"), status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['GET'])
    def is_thumbs_up(self, request):
        """
        查看用户对此作品是否点赞{"userdubbing":1,"user":1}
        """
        user = request.GET.get('user')
        userdubbing = request.GET.get('userdubbing')
        if (not user) or (not userdubbing):
            return Response({"message": "user和userdubbing为必须传入的字段！", "code": 400, "data": False},
                            status=status.HTTP_200_OK)
        dz_list = DubbingZan.objects.filter(userdubbing=userdubbing, user=user)
        if dz_list:
            return Response({"data": True, "code": 200, "message": "success"}, status=status.HTTP_200_OK)
        return Response({"data": False, "code": 200, "message": "success"}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_ranking_list(self, request):
        """
        点赞排名:type不传默认为0，全服；传1班级；传2学校，传3区域
        """
        is_competition = request.GET.get("is_competition", 0)
        if str(is_competition) == "1":
            is_competition = True
        else:
            is_competition = False
        user = request.user
        default_cid = user.profile.default_cid
        rank_type = request.GET.get("area", 0)
        school = user.profile.school()
        # area = request.GET.get("area", 0)
        if rank_type == '0' or rank_type == 0:
            user_list = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition).exclude(
                is_active=False).order_by().values('user').distinct()
        elif rank_type == '1' or rank_type == 1:
            ul = BigfishUser.objects.filter(default_cid=default_cid).values('user').distinct()
            user_list = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user__in=ul,
                                                   is_active=True).values('user').distinct()
        elif rank_type == '2' or rank_type == 2:
            ul = BigfishUser.objects.filter(attend_class__school=school, identity="学生").values('user').distinct()
            user_list = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user__in=ul,
                                                   is_active=True).values('user').distinct()
            # user_list = UserDubbing.objects.filter(user__profile__area=area, is_active=True).values('user').\
            #                 distinct()
        elif rank_type == '3' or rank_type == 3:
            sl = School.objects.filter(area=school.area)
            ul = BigfishUser.objects.filter(attend_class__school__in=sl, identity="学生").values('user').distinct()
            user_list = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user__in=ul,
                                                   is_active=True).values('user').distinct()
        else:
            return Response({"message": "type error", "code": 400, "data": []},
                            status=status.HTTP_200_OK)
        rank_list = []
        for item in user_list:
            tmp_dict = OrderedDict({'user': item['user']})
            zan = DubbingZan.objects.filter(userdubbing__user=item['user'], userdubbing__is_active=True,
                                            userdubbing__dubbingsrc__is_competition=is_competition). \
                values('userdubbing', 'userdubbing__description', 'userdubbing__create_time').annotate(
                num_zan=Count('user')).order_by('-num_zan', 'userdubbing__create_time')
            if zan:
                tmp_dict.update(zan[0])
            else:
                tmp_dict['num_zan'] = 0
                user_id = item['user']
                if rank_type == '0' or rank_type == 0:
                    ud_obj = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user=item['user'],
                                                        is_active=True).first()
                elif rank_type == '1' or rank_type == 1:
                    ul = BigfishUser.objects.filter(default_cid=default_cid).values('user').distinct()
                    ud_obj = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user__in=ul,
                                                        user=item['user'], is_active=True).first()
                elif rank_type == '2' or rank_type == 2:
                    ul = BigfishUser.objects.filter(attend_class__school=school, identity="学生").values(
                        'user').distinct()
                    ud_obj = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user__in=ul,
                                                        user=item['user'], is_active=True).first()
                elif rank_type == '3' or rank_type == 3:
                    sl = school.objects.filter(area=school.area)
                    ul = BigfishUser.objects.filter(attend_class__school__in=sl, identity="学生").values(
                        'user').distinct()
                    ud_obj = UserDubbing.objects.filter(dubbingsrc__is_competition=is_competition, user__in=ul,
                                                        user=item['user'], is_active=True).first()
                # else:
                #    ud_obj = UserDubbing.objects.filter(user__profile__area=area, user=item['user'], is_active=True).\
                #        first()
                tmp_dict['userdubbing'] = ud_obj.id
                tmp_dict['userdubbing__description'] = ud_obj.description
                tmp_dict['userdubbing__create_time'] = ud_obj.create_time
            try:
                zan_obj = DubbingZan.objects.get(userdubbing=tmp_dict['userdubbing'], user=user)
                tmp_dict['is_zan'] = True
            except Exception as e:
                tmp_dict['is_zan'] = False
            rank_list.append(tmp_dict)
        rank_list.sort(key=lambda e: (-e['num_zan'], e['userdubbing__create_time']))
        rank_list = rank_list[:100]
        owner = request.user
        owner_info = {}
        for r in rank_list:
            try:
                ub = UserDubbing.objects.get(dubbingsrc__is_competition=is_competition, id=r['userdubbing'],
                                             is_active=True)
            except Exception as e:
                # print(e)
                continue
            try:
                user = User.objects.get(id=r['user'])
            except Exception as e:
                # print(e)
                continue
            r['username'] = user.username
            r['nickname'] = user.profile.nickname
            r['realname'] = user.profile.realname
            r['icon'] = user.profile.icon
            if ub.video:
                r['voide'] = ub.video.url
            else:
                r['voide'] = ""
            if owner.id == r['user']:
                user_ranking_num = [rank_list.index(x) for x in rank_list if x['user'] == owner.id][0] + 1
                owner_info['user'] = r['user']
                owner_info['num_zan'] = r['num_zan']
                owner_info['userdubbing'] = r['userdubbing']
                owner_info['is_zan'] = r['is_zan']
                owner_info['username'] = owner.username
                owner_info['nickname'] = owner.profile.nickname
                owner_info['realname'] = owner.profile.realname
                owner_info['icon'] = owner.profile.icon
                owner_info['voide'] = r['voide']
                owner_info['ranking_num'] = user_ranking_num
        data = {'rank_list': rank_list, 'owner_info': owner_info}
        return Response(rsp_msg_200(data), status=status.HTTP_200_OK)

    # return Response({"results": rank_list, "code": 200}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def zan_user_list(self, request):
        """
        xx配音作品点赞用户信息

        :param request: \n
            userdubbing=1[&page_size=10][&page=1]
        :return: \n
            {

            }
        """
        user_list = self.filter_queryset(self.get_queryset()).values_list("user_id", flat=True)
        queryset = BigfishUser.objects.filter(id__in=user_list)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MinUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MinUserSerializer(queryset, many=True)
        return Response(rsp_msg_200(serializer.data))


class DubbingReadViewSet(viewsets.ModelViewSet):
    serializer_class = DubbingReadSerializer
    queryset = DubbingRead.objects.all()
    filter_fields = ('id', 'user',)


class CompetitionViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        返回配音大赛实例。
    list:
        返回最近加入的所有配音大赛。
    create:
        创建一个新的配音大赛。
    delete:
        删除现有的配音大赛。
    partial_update:
        更新现有配音大赛中的一个或多个字段。
    update:
        更新配音大赛。
    """
    serializer_class = CompetitionSerializer
    queryset = Competition.objects.all()
    filter_fields = ('id', 'title', 'user', 'order', 'is_active', 'banner')

    @list_route(methods=["get"])
    def get_latest_competition(self, request):
        """
        获取默认配音大赛信息（最新一届）

        :param request: \n
        :return: \n
            {
              "message": "success",
              "code": 200,
              "data": {
                "title": "test",
                "content": "",
                "notice": "",
                "user": null,
                "start_date": "2018-05-02",
                "end_date": "2018-05-02",
                "order": 0,
                "is_active": true,
                "add_time": "2018-05-02T18:01:10.121607",
                "banner": []
              }
            }
        """
        queryset = Competition.objects.filter(is_active=True).order_by('-order').first()
        ret_data = CompetitionSerializer(queryset).data
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class SubCompetitionViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        返回配音大赛分赛区实例。
    list:
        返回最近加入的所有配音大赛分赛区。
    create:
        创建一个新的配音大赛分赛区。
    delete:
        删除现有的配音大赛分赛区。
    partial_update:
        更新现有配音大赛分赛区中的一个或多个字段。
    update:
        更新配音大赛分赛区。
    """
    serializer_class = SubCompetitionSerializer
    queryset = SubCompetition.objects.all()
    filter_fields = ('id', 'user', 'area', 'school', 'grade', 'klass', 'competition', 'is_active')

    @list_route(methods=["get"])
    def get_latest_sub_competition(self, request):
        """
        获取默认配音大赛分赛区信息（最新一届）

        :param request: \n
        :return: \n
            {
              "message": "success",
              "data": {
                "title": "test",
                "content": "",
                "notice": "",
                "user": null,
                "start_date": "2018-05-02",
                "end_date": "2018-05-02",
                "order": 2,
                "category": 1,
                "is_active": true,
                "add_time": "2018-05-02T18:01:10.121607",
                "banner": [
                  1,
                  2,
                  3
                ],
                "banner_data": [
                  {
                    "id": 1,
                    "title": "test",
                    "img_type": 1,
                    "img": "/media/dubbing/unknown/7864a8bbf007f857bf1f889b2062746c.jpg",
                    "add_time": "2018-05-25T15:47:47.197000"
                  },
                  {
                    "id": 2,
                    "title": "fasfaf",
                    "img_type": 2,
                    "img": "/media/dubbing/unknown/b_64.png",
                    "add_time": "2018-05-25T15:49:21.225000"
                  },
                  {
                    "id": 3,
                    "title": "asdasd",
                    "img_type": 3,
                    "img": "/media/dubbing/unknown/ee57c2ad933aabb5f0030e7ade8a5308.jpg",
                    "add_time": "2018-05-25T15:49:29.175000"
                  }
                ],
                "sub_competition": {
                  "competition": 4,
                  "area_competition": null,
                  "area": 1,
                  "school": 2,
                  "grade": 11,
                  "klass": 1,
                  "user": 18,
                  "prepare_time": "2018-05-03T14:21:00",
                  "competing_time": "2018-05-03T14:21:00",
                  "end_time": "2018-05-03T14:21:00",
                  "is_active": true,
                  "add_time": "2018-05-03T14:24:20.666000",
                  "dubbingsrc": [
                    1
                  ]
                }
              },
              "code": 200
            }
        """
        user = request.user
        competition_qs = Competition.objects.filter(is_active=True).order_by('-order')
        if competition_qs.count() == 0:
            raise BFValidationError("未查询到有任何配音大赛信息！")
        competition_obj = competition_qs.first()
        competition_data = CompetitionSerializer(competition_obj).data
        # 全服
        if competition_obj.category == 1:
            try:
                sub_competition = SubCompetition.objects.get(competition=competition_obj.id)
            except Exception as e:
                raise BFValidationError("获取配音大赛信息失败！【{}】".format(e))
        else:
            try:
                user = BigfishUser.objects.get(user=user.id)
            except Exception as e:
                raise BFValidationError("未获取到用户信息！【{}】".format(e))
            try:
                klass = Klass.objects.get(id=int(user.default_cid))
            except Exception as e:
                raise BFValidationError("查询用户班级信息失败！【{}】".format(e))
            # 地区
            if competition_obj.category == 2:
                try:
                    sub_competition = SubCompetition.objects.get(competition=competition_obj.id,
                                                                 area=klass.school.areas)
                except Exception as e:
                    raise BFValidationError("还未开启过大赛，敬请期待！")
            # 年级
            elif competition_obj.category == 3:
                grade_choice = dict(SubCompetition.GRADE_CHOICES)
                grade = [k for k, v in grade_choice.items() if v == klass.grade][0]
                try:
                    sub_competition = SubCompetition.objects.get(competition=competition_obj.id, grade=grade)
                except Exception as e:
                    raise BFValidationError("还未开启过大赛，敬请期待！")
            # 其他(学校，暂时不考虑班级)
            elif competition_obj.category == 4:
                try:
                    sub_competition = SubCompetition.objects.get(competition=competition_obj.id, school=klass.school)
                except Exception as e:
                    raise BFValidationError("还未开启过大赛，敬请期待！")
            else:
                raise BFValidationError("配置信息异常！")
        sub_competition_data = SubCompetitionSerializer(sub_competition).data
        competition_data['sub_competition'] = sub_competition_data
        return Response(rsp_msg_200(competition_data), status=status.HTTP_200_OK)


class CompetitionRankViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        返回配音大赛排名实例。
    list:
        返回最近加入的所有配音大赛排名。
    create:
        创建一个新的配音大赛排名。
    delete:
        删除现有的配音大赛排名。
    partial_update:
        更新现有配音大赛排名中的一个或多个字段。
    update:
        更新配音大赛排名。
    """
    serializer_class = CompetitionRankSerializer
    queryset = CompetitionRank.objects.all()
    filter_fields = (
        'id', 'user', 'competition', 'area_id', 'school_id', 'class_id', 'user_dubbing', 'rank', 'is_receive_award',
        'bf_coin', 'zan_num')

    @list_route()
    def competition_settlement(self, request):
        """
        配音大赛结算

        :param request:\n
            ?competition_id=4
        :return:\n
            {
                "message": "success",
                "code": 200,
                "data": [
                    {
                        "competition": 4,
                        "user": 18,
                        "realname": "张三",
                        "area_id": 2840,
                        "school_id": 2,
                        "class_id": 1,
                        "area": "陕西省西安市莲湖区",
                        "school": "",
                        "klass": "高新一中小学二年级1",
                        "user_dubbing": 4,
                        "rank": 1,
                        "is_receive_award": false,
                        "bf_coin": 8000,
                        "zan_num": 2,
                        "add_time": "2018-05-26T17:58:41.243000"
                    },
                    {
                        "competition": 4,
                        "user": 19,
                        "realname": "李四",
                        "area_id": 2840,
                        "school_id": 2,
                        "class_id": 1,
                        "area": "陕西省西安市莲湖区",
                        "school": "",
                        "klass": "高新一中小学二年级1",
                        "user_dubbing": 5,
                        "rank": 2,
                        "is_receive_award": false,
                        "bf_coin": 7500,
                        "zan_num": 1,
                        "add_time": "2018-05-26T17:58:41.258000"
                    }
                ]
            }
        """
        competition_id = request.GET.get("competition_id", None)
        try:
            competition_obj = Competition.objects.get(id=competition_id)
        except Exception as e:
            raise BFValidationError("获取配音大赛信息失败！【{}】".format(e))
        ret_data = competition_settlement(competition_obj)
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class RewardConfigViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        返回配音大赛奖励规则实例。
    list:
        返回所有配音大赛奖励规则。
    create:
        创建一个新的配音大赛奖励规则。
    delete:
        删除现有的配音大赛奖励规则。
    partial_update:
        更新现有配音大赛奖励规则中的一个或多个字段。
    update:
        更新配音大赛奖励规则。
    """
    serializer_class = RewardConfigSerializer
    queryset = RewardConfig.objects.all()
    filter_fields = ('competition__title', 'competition__order')

    @list_route(methods=['GET'])
    def get_reward_config(self, request):
        """
        获取配音大赛奖励配置信息

        :param request:\n
            ?competition_id=2
        :return:\n
            {
                "data": {
                    "competition": 2,
                    "reward_data": {
                        "ranking_reward": [
                            {
                                "ranking": 1,
                                "reward": 2000
                            },
                            {
                                "ranking": 2,
                                "reward": 1500
                            },
                            {
                                "ranking": 3,
                                "reward": 1000
                            },
                            {
                                "ranking": 4,
                                "reward": 500
                            },
                            {
                                "ranking": 5,
                                "reward": 400
                            },
                            {
                                "ranking": 6,
                                "reward": 300
                            },
                            {
                                "ranking": 7,
                                "reward": 200
                            }
                        ],
                        "participation_reward": 100
                    }
                },
                "code": 200,
                "message": "success"
            }
        """
        competition_id = request.GET.get("competition_id")
        try:
            rc_obj = RewardConfig.objects.get(competition=competition_id)
        except Exception as e:
            raise BFValidationError("获取奖励配置信息失败！【{}】".format(e))
        ret_data = RewardConfigSerializer(rc_obj).data
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((Everyone,))
def wx_share_view(request):
    userdubbing = request.GET.get('userdubbing')
    results = []
    try:
        ud_obj = UserDubbing.objects.get(id=userdubbing, is_active=True)
    except Exception as e:
        # print(e)
        return Response({"detail": "userdubbing没有查找到！", "code": 400}, status=status.HTTP_200_OK)
    dubbing_data = UserDubbingSerializer(ud_obj).data
    ud_list = UserDubbing.objects.filter(is_active=True)[0:2]
    for ud in ud_list:
        data = UserDubbingSerializer(ud).data
        results.append(data)
    return Response({"results": results, "detail": dubbing_data, "code": 300}, status=status.HTTP_200_OK)
