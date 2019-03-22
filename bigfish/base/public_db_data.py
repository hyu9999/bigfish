from bigfish.apps.areas.models import Area
from bigfish.apps.schools.models import Klass
from bigfish.apps.users.models import UserKlassRelationship
from bigfish.base.response import BFValidationError


def get_question_data(request):
    """答题详情数据 (AbsActDataRpt)"""
    question_dict = {
        'answer_right_times': request.data.get('answer_right_times', 0),
        'answer_wrong_time': request.data.get('answer_wrong_time', 0),
        'answer_max': request.data.get('answer_max', 0),
        'question_total_num': request.data.get('question_total_num', 0),
        'all_time': request.data.get('all_time', 0),
        'is_complete': request.data.get('is_complete', False),
        'right_rate': request.data.get('right_rate', 0.0),
        'max_right_number': request.data.get('max_right_number', 0),
        'score': request.data.get('score', 0),
    }
    return question_dict


def get_question_report(request):
    """题目详情数据 （AbsQuestionRpt）"""
    question_report_dict = {
        'question_id': request.data.get('question_id', ''),
        'is_right': request.data.get('is_right', False),
        'question_type': request.data.get('question_type', ''),
        'difficulty': request.data.get('difficulty', 10),
        'voice_url': request.data.get('voice_url', ''),
        'answer': request.data.get('answer', {}),
        'purpose': request.data.get('purpose', ''),
    }
    return question_report_dict


def get_publish_data(activity):
    """教材数据 (AbsPublishRpt)"""
    publish_data = {
        'publish_name': activity.publish.title,
        'textbook_name': activity.textbook.title,
        'textbook_id': activity.textbook.id,
        'term_num': activity.textbook.term,
        'unit_name': activity.unit.title,
        'lesson_name': activity.lesson.title,
        'lesson_order': activity.lesson.order
    }
    return publish_data


def get_user_data(request):
    """用户数据 (AbsPersonalRpt)"""
    user = request.user
    klass_id = request.data.get('klass_id', None)
    if klass_id is None:
        try:
            user_klass = UserKlassRelationship.objects.get(user=user, is_default=True)
        except:
            raise BFValidationError('用户没有默认班级')
        klass = user_klass.klass
    else:
        try:
            klass = Klass.objects.get(id=klass_id)
        except:
            raise BFValidationError('班级id不存在')
    try:
        city = Area.objects.get(coding=klass.school.areas.city_code)
        prov = Area.objects.get(coding=klass.school.areas.prov_code)
    except:
        raise BFValidationError('班级配置的地区有误')
    user_data = {
        'username': user.username,
        'realname': user.realname,
        'nickname': user.nickname,
        'klass_id': klass.id,
        'klass_name': klass.title,
        'grade_name': klass.grade,
        'school_id': klass.school.id,
        'school_name': klass.school.title,
        'short_name': klass.school.short_name,
        'area_id': klass.school.areas.coding,
        'area_name': klass.school.areas.name,
        'city_name': city.name,
        'city_code': klass.school.areas.city_code,
        'province_name': prov.name,
        'province_code': klass.school.areas.prov_code,
    }
    return user_data


def get_act_data(activity):
    """活动数据 (AbsActRpt)"""
    activity_data = {
        'first_type': activity.act_type.first_type,
        'first_type_name': activity.act_type.get_first_type_display(),
        'second_type': activity.act_type.second_type,
        'second_type_name': activity.act_type.get_second_type_display(),
        'third_type': activity.act_type.third_type,
        'act_title': activity.title,
        'act_subtitle': activity.subtitle
    }
    return activity_data