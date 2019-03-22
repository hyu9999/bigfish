import datetime
import json
import logging

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.visualbackend.backend.commons import get_user_basic_data, get_current_school_term, get_klass_list, \
    get_current_term
from django.db.models import Count, Avg, F
from bigfish.apps.users.models import UserProfile
from bigfish.apps.schools.models import Task, Lesson
from bigfish.apps.visualbackend.models import TeacherData

logger = logging.getLogger('django')


def write_to_teacher_data(term):
    # klass list
    klass_list = get_klass_list()
    for klass in klass_list:
        # teacher list
        teacher_list = UserProfile.objects.filter(identity="老师", attend_class=klass)
        school_id = klass.school_id
        school_term = get_current_school_term(school_id, term)
        if school_term:
            query_duration = [school_term.start_date, school_term.finish_date]
        else:
            query_duration = [term.start_date, term.finish_date]
        for user_profile in teacher_list:
            # basic info
            basic_info = get_user_basic_data(user_profile)
            if school_term:
                basic_info['school_term'] = school_term
            kwargs = {"term": term, "klass_id": basic_info.get("klass_id"),
                      "username": basic_info.get("username")}
            # compute data
            compute_data = get_teacher_compute_data(klass, user_profile.user, query_duration)
            if not TeacherData.objects.filter(**kwargs).exists():
                compute_data.update(basic_info)
            try:
                TeacherData.objects.update_or_create(defaults=compute_data, **kwargs)
            except Exception as e:
                logger.exception("error_msg:{};\n filter_data:{}\ncompute_data:{}".format(e, kwargs, compute_data))


def get_teacher_compute_data(klass, user, query_duration):
    ret_data = {}
    """
    根据教师端统计的交互时间轴进行统计
    这个时间轴的开始时间到结尾时间之间的时间差则为一次教师端使用的总用时
    """
    in_use = False
    queryset = Task.objects.filter(open_date__date__range=query_duration, klass=klass,
                                   user=user)
    if queryset.exists():
        in_use = True
        # TODO 暂无计算方法 :计算任务平均使用时长
        use_duration = queryset.aggregate(data=Avg(F('close_date') - F('open_date'))).get('data').total_seconds()
        ret_data["use_duration"] = use_duration
        """
        教师发出的任务ID: 根据任务ID统计任务中统计的活动数量
        """
        push_activity_num = 0
        task_num = queryset.count()
        ret_data["task_num"] = task_num
        for task in queryset:
            try:
                act_num = len(json.loads(task.sequence_list))
            except Exception as e:
                act_num = 0
            push_activity_num += act_num
        ret_data["push_activity_num"] = push_activity_num
        """
        筛选出这个老师在任务中发布过的最大Unit-Lesson值，通过这个值算出这个老师自己的教学进度百分比
        """
        progress_obj = queryset.filter(lesson__order__lt=100).order_by('unit__order', 'lesson__order').last()
        if progress_obj:
            textbook = progress_obj.unit.textbook
            total_lesson = Lesson.objects.filter(unit__textbook=textbook).aggregate(data=Count('id')).get('data')
            unit_lesson = Lesson.objects.filter(unit__textbook=textbook,
                                                unit__order__gt=progress_obj.lesson.unit.order).aggregate(
                data=Count('id')).get('data')
            lesson = Lesson.objects.filter(unit__textbook=textbook, unit=progress_obj.unit,
                                           order__lte=progress_obj.lesson.order).aggregate(
                data=Count('id')).get('data')
            teaching_progress = round(float(unit_lesson + lesson) / total_lesson, 10)
        else:
            teaching_progress = 0
        ret_data["teaching_progress"] = teaching_progress
    ret_data["in_use"] = in_use
    return ret_data


if __name__ == '__main__':
    """
    写入studentData表数据
    """
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    write_to_teacher_data(t)
