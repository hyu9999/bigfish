import logging

from django.db import transaction
from django.db.models import Count, F

from bigfish.apps.areas.models import Area
from bigfish.apps.dubbing.models import Competition, RewardConfig, CompetitionRank, SubCompetition, DubbingZan, \
    UserDubbing
from bigfish.apps.dubbing.serializers import CompetitionRankSerializer
from bigfish.apps.users.models import BigfishUser, BigfishUser
from bigfish.apps.schools.models import Klass, School
from bigfish.base.response import BFValidationError

logger = logging.getLogger('django')


def auto_settlement():
    ret_data = []
    competition_list = Competition.objects.filter(is_settle=False, is_active=True)
    if not competition_list.exists():
        return
    for item in competition_list:
        tmp_data = competition_settlement(item)
        ret_data.append(tmp_data)


def competition_settlement(competition_obj):
    with transaction.atomic():
        ret_data = []
        if competition_obj.is_settle is True:
            raise BFValidationError("该赛事已经结算过！")
        competition_obj.is_settle = True
        competition_obj.save()
        try:
            reward_conf_obj = RewardConfig.objects.get(competition=competition_obj)
        except Exception as e:
            raise BFValidationError("查询奖励配置信息失败！【{}】".format(e))
        else:
            reward_conf = reward_conf_obj.reward_data
            ranking_reward = reward_conf.get("ranking_reward", [])
            rank_len = len(ranking_reward)
            participation_reward = reward_conf.get("participation_reward", 0)
            zan_list = competition_zan_ranking(competition_obj)
            for index, item in enumerate(zan_list):
                rank = index + 1
                if rank > rank_len:
                    bf_coin = participation_reward
                else:
                    bf_coin = ranking_reward[index].get("reward", participation_reward)
                kwargs = {"rank": rank, "bf_coin": bf_coin, "competition": competition_obj}
                fmt_data = format_str(item)
                kwargs.update(fmt_data)

                try:
                    obj = CompetitionRank.objects.create(**kwargs)
                except Exception as e:
                    raise BFValidationError("写入排行榜数据失败！【{}】".format(e))
                else:
                    ret_data.append(CompetitionRankSerializer(obj).data)
    return ret_data


def competition_zan_ranking(competition_obj):
    dubbing_src_list = get_dubbing_src_list(competition_obj)
    userdubbing = UserDubbing.objects.filter(dubbingsrc__in=dubbing_src_list)
    ret_list = []
    dubbing_zan_list = DubbingZan.objects.filter(userdubbing__in=userdubbing).order_by(
        "userdubbing__dubbingsrc").values(
        "userdubbing__dubbingsrc").annotate(zan_num=Count("userdubbing"),
                                            user_id=F("userdubbing__user"),
                                            user_dubbing_id=F("userdubbing__id"),
                                            realname=F("userdubbing__user__profile__realname"),
                                            area_id=F("userdubbing__user__profile__attend_class__school__areas"),
                                            school_id=F("userdubbing__user__profile__attend_class__school"),
                                            school=F("userdubbing__user__profile__attend_class__school__name"),
                                            class_id=F("userdubbing__user__profile__attend_class")
                                            ).values("user_id", "user_dubbing_id",
                                                     "realname", "area_id",
                                                     "school_id",
                                                     "class_id",
                                                     "zan_num").order_by("-zan_num")
    tmp_user_list = []
    for item in dubbing_zan_list:
        if item['user_id'] in tmp_user_list:
            continue
        ret_list.append(item)
        tmp_user_list.append(item['user_id'])
    user_id_list = [x['user_id'] for x in dubbing_zan_list]
    other_rank_list = userdubbing.exclude(user__in=user_id_list).order_by('user', 'create_time')
    tmp_user_list = []
    for item in other_rank_list:
        if item.user.id in tmp_user_list:
            continue
        tmp_dict = {"zan_num": 0,
                    "user_id": item.user.id,
                    "user_dubbing_id": item.id,
                    "realname": item.user.profile.realname
                    }
        class_list = item.user.profile.attend_class.all()
        if class_list.exists():
            tmp_dict["area_id"] = class_list.first().school.areas.id
            tmp_dict["school_id"] = class_list.first().school.id
            tmp_dict["school"] = class_list.first().school.name
            tmp_dict["class_id"] = class_list.first().id
        ret_list.append(tmp_dict)
        tmp_user_list.append(item.user.id)
    return ret_list


def get_dubbing_src_list(competition_obj):
    sub_competition = SubCompetition.objects.filter(competition=competition_obj)
    dubbing_src_list = []
    for item in sub_competition:
        tmp_list = item.dubbingsrc.values_list('id', flat=True)
        dubbing_src_list.extend(tmp_list)
    dubbing_src_list = list(set(dubbing_src_list))
    return dubbing_src_list


def format_str(str_dict):
    user_id = str_dict.get("user_id")
    str_dict.pop("user_id", None)
    try:
        user = BigfishUser.objects.get(user=user_id).user
    except Exception as e:
        user = None
    str_dict["user"] = user
    # area
    area_id = str_dict.get("area_id")
    try:
        area = Area.objects.get(id=area_id)
    except Exception as e:
        area = ""
    else:
        area = area.__str__()
    str_dict["area"] = area
    # school
    school_id = str_dict.get("school_id")
    try:
        school = School.objects.get(id=school_id)
    except Exception as e:
        school = ""
    else:
        school = school.__str__()
    str_dict["school"] = school
    # class
    class_id = str_dict.get("class_id")
    try:
        klass = Klass.objects.get(id=class_id)
    except Exception as e:
        klass = ""
    else:
        klass = klass.__str__().replace(" ", "")
    str_dict["klass"] = klass
    return str_dict
