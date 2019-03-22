import datetime

from django.db.models import Count, Sum, F, FloatField, Max
from rest_framework.exceptions import ValidationError

from bigfish.apps.reports.models import StudentDailyData, KlassDailyData, SchoolDailyData, PracticalCourseRecord, \
    SaveDataInfo, EnterStudy, ActivityDailyData
from bigfish.apps.reports.serializers import PracticalCourseRecordSerializer
from bigfish.apps.research.models import TeacherSchedule
from bigfish.apps.users.models import UserProfile
from bigfish.apps.schools.models import School, Klass, Task, Lesson, ActType, Activity, Textbook
import logging

from bigfish.utils.functions import get_key_by_value

logger = logging.getLogger('django')


def daily_data_to_db(search_data=datetime.datetime.now().date()):
    collect_school_data(search_data)
    # collect_act_type_data(search_data)


def get_task_textbook(current_date, klass_obj):
    current_month = current_date.month
    if current_month in range(3, 8):
        term_num = 2
    else:
        term_num = 1
    grade = get_key_by_value(Textbook.GRADE_CHOICES, klass_obj.get_grade_display())
    textbook = Textbook.objects.filter(term_num=term_num, publish=klass_obj.publish, grade=grade).first()
    return textbook


def get_klass_ul(klass_obj, current_date):
    textbook = get_task_textbook(current_date, klass_obj)
    final_obj = Task.objects.filter(open_date__date__lte=current_date, klass=klass_obj, textbook=textbook.id,
                                    lesson__order__lt=100).order_by('unit__order', 'lesson__order').last()
    if not final_obj:
        return 0, 0, 0
    else:
        # 获取lesson总数
        textbook = final_obj.textbook
        try:
            lesson_list = Lesson.objects.filter(unit__textbook=textbook)
            lesson_dict = lesson_list.values('unit').annotate(cnt_lesson=Count('unit'))
            ano_data = lesson_dict.aggregate(sum_lesson=Sum('cnt_lesson'))
        except Exception as e:
            total_ul = 0
        else:
            total_ul = ano_data.get('sum_lesson')
        # 获取最大lesson
        try:
            unit_num = final_obj.unit.order
            lesson_list = Lesson.objects.filter(unit__textbook=textbook, unit__order__lt=unit_num).count()
            lesson_num = final_obj.lesson.order
            max_ul = int(lesson_list) + int(lesson_num)
        except Exception as e:
            max_ul = 0
        try:
            avg_ul = round(max_ul / int(total_ul) * 100)
        except Exception as e:
            k_kwargs = {"record_date": current_date, "klass": klass_obj}
            avg_ul = KlassDailyData.objects.filter(**k_kwargs).aggregate(max_avg_ul=Max('avg_ul')).get(
                'max_avg_ul')
            if avg_ul is None:
                avg_ul = 0
        return max_ul, total_ul, avg_ul


def get_use_duration(klass_obj, current_date):
    pcr_num = PracticalCourseRecord.objects.filter(klass=klass_obj, teaching_date=current_date).count()
    queryset = Task.objects.filter(klass=klass_obj, open_date__date=current_date)
    if queryset.exists():
        use_duration = queryset.aggregate(sum_time=Sum(F('finish_time') - F('open_date'))).get(
            "sum_time").total_seconds()
    else:
        use_duration = 0
    return use_duration, pcr_num


def collect_school_data(search_data):
    school_list = School.objects.filter(is_normal=True).order_by('id')
    for school_obj in school_list:
        if school_obj.id != 46:
            continue
        s_kwargs = {"record_date": search_data, "school": school_obj}  # search condition
        max_avg_ul = SchoolDailyData.objects.filter(record_date__lt=search_data, school=school_obj).aggregate(
            max_avg_ul=Max('avg_ul')).get('max_avg_ul')
        if max_avg_ul is None:
            max_avg_ul = 0
        ss_list = []
        scn_list = []
        sd_list = []
        sn_list = []
        sau_list = []
        sud_list = []
        scrn_list = []
        klass_list = Klass.objects.filter(school=school_obj)
        if not klass_list.exists():
            s_defaults = {"score": 0, "complete_num": 0, "duration": 0, "num": 0,
                          "avg_ul": max_avg_ul, "use_duration": 0, "course_num": 0}
            # SchoolDailyData.objects.update_or_create(defaults=s_defaults, **s_kwargs)
            continue
        for klass_obj in klass_list:
            # if klass_obj.id != 114:
            #     continue
            ks_list = []
            kcn_list = []
            kd_list = []
            kn_list = []
            user_list = UserProfile.objects.filter(default_cid=str(klass_obj.id))
            if not user_list.exists():
                continue
            for user_obj in user_list:
                queryset = SaveDataInfo.objects.filter(add_time__date=search_data, user=user_obj.user)
                study_queryset = EnterStudy.objects.filter(end_time__date=search_data, owner=user_obj.user)
                if (not queryset.exists()) and (not study_queryset.exists()):
                    continue
                complete_queryset = queryset.filter(
                    answer_max=F('answer_right_times') + F('answer_wrong_time')).exclude(answer_max=0)
                # get score and complete number
                complete_num = complete_queryset.count()
                kcn_list.append(complete_num)
                if complete_num == 0:
                    score = 0
                else:
                    score = complete_queryset.aggregate(
                        sum_score=Sum(F('answer_right_times') * 1.0 / F('answer_max') * 100.0)).get("sum_score")
                    if score is None:
                        score = 0
                ks_list.append(score)

                # get duration and number
                if not queryset.exists():
                    p_duration = 0
                    p_num = 0
                else:
                    p_duration = queryset.aggregate(Sum("all_time")).get("all_time__sum")
                    p_num = queryset.count()
                if not study_queryset.exists():
                    s_duration = 0
                    s_num = 0
                else:
                    s_duration = study_queryset.aggregate(sum_time=Sum(F("end_time") - F("start_time"))).get(
                        "sum_time").total_seconds()
                    s_num = study_queryset.count()
                try:
                    duration = int(p_duration) + int(s_duration) * 1000
                except Exception as e:
                    raise ValidationError("1====={}".format(e))
                kd_list.append(duration)
                try:
                    num = int(p_num) + int(s_num)
                except Exception as e:
                    raise ValidationError("2====={}".format(e))
                kn_list.append(num)
                defaults = {"score": score, "complete_num": complete_num, "duration": duration, "num": num}
                kwargs = {"record_date": search_data, "student": user_obj.user}  # search condition
                # StudentDailyData.objects.update_or_create(defaults=defaults, **kwargs)
            # class
            max_ul, total_ul, avg_ul = get_klass_ul(klass_obj, search_data)
            sau_list.append(avg_ul)
            if not ks_list:
                k_kwargs = {"record_date": search_data, "klass": klass_obj}  # search condition
                k_max_avg_ul = KlassDailyData.objects.filter(record_date__lt=search_data, klass=klass_obj).aggregate(
                    max_avg_ul=Max('avg_ul')).get('max_avg_ul')
                if k_max_avg_ul is None:
                    k_max_avg_ul = 0
                k_defaults = {"score": 0, "complete_num": 0, "duration": 0, "num": 0,
                              "max_ul": 0, "total_ul": 0, "avg_ul": k_max_avg_ul, "use_duration": 0,
                              "course_num": 0}

                # KlassDailyData.objects.update_or_create(defaults=k_defaults, **k_kwargs)
                continue
            k_score = sum(ks_list)
            ss_list.append(k_score)
            k_complete_num = sum(kcn_list)
            scn_list.append(k_complete_num)
            k_duration = sum(kd_list)
            sd_list.append(k_duration)
            k_num = sum(kn_list)
            sn_list.append(k_num)
            use_duration, course_num = get_use_duration(klass_obj, search_data)
            sud_list.append(use_duration)
            scrn_list.append(course_num)
            k_defaults = {"score": k_score, "complete_num": k_complete_num, "duration": k_duration, "num": k_num,
                          "max_ul": max_ul, "total_ul": total_ul, "avg_ul": avg_ul, "use_duration": use_duration,
                          "course_num": course_num}
            k_kwargs = {"record_date": search_data, "klass": klass_obj}  # search condition
            # KlassDailyData.objects.update_or_create(defaults=k_defaults, **k_kwargs)
        # school
        if not ss_list:
            s_defaults = {"score": 0, "complete_num": 0, "duration": 0, "num": 0,
                          "avg_ul": max_avg_ul, "use_duration": 0, "course_num": 0}
            # SchoolDailyData.objects.update_or_create(defaults=s_defaults, **s_kwargs)
            continue
        s_score = sum(ss_list)
        s_complete_num = sum(scn_list)
        s_duration = sum(sd_list)
        s_num = sum(sn_list)
        try:
            s_avg_ul = round(sum(sau_list) / len(sau_list))
        except Exception as e:
            s_avg_ul = 0
        s_use_duration = sum(sud_list)
        s_course_num = sum(scrn_list)
        s_defaults = {"score": s_score, "complete_num": s_complete_num, "duration": s_duration, "num": s_num,
                      "avg_ul": s_avg_ul, "use_duration": s_use_duration, "course_num": s_course_num}
        # SchoolDailyData.objects.update_or_create(defaults=s_defaults, **s_kwargs)


def collect_act_type_data(search_data):
    school_list = School.objects.filter(is_normal=True).order_by('id')
    for school_obj in school_list:
        if school_obj.id != 52:
            continue
        klass_list = Klass.objects.filter(school=school_obj)
        if not klass_list.exists():
            continue
        for klass_obj in klass_list:
            if klass_obj.id != 114:
                continue
            user_list = UserProfile.objects.filter(default_cid=str(klass_obj.id)).values_list('user__id', flat=True)
            act_type_list = ActType.objects.all()
            for act_type in act_type_list:
                if act_type.name != '词汇学习':
                    continue
                act_list = Activity.objects.control().filter(act_type=act_type).values_list("id", flat=True)

                kwargs = {"record_date": search_data, "school_id": school_obj.id,
                          "school_name": school_obj.name, "klass_id": klass_obj.id,
                          "klass_name": "{}{}".format(klass_obj.get_grade_display(), klass_obj.name),
                          "act_type_id": act_type.id, "act_type_name": act_type.name,
                          "study_type": act_type.study_type}  # search condition
                # practice
                if act_type.study_type == 1:
                    queryset = SaveDataInfo.objects.filter(add_time__date=search_data, user__in=user_list,
                                                           sort_type=act_type.name)
                    num = len(queryset.values())
                    complete_queryset = queryset.filter(
                        answer_max=F('answer_right_times') + F('answer_wrong_time')).exclude(answer_max=0)
                    score = complete_queryset.aggregate(
                        total_score=Sum(F('answer_right_times') * 1.0 / F('answer_max') * 100.0,
                                        output_field=FloatField())).get("total_score")
                    if score is None:
                        score = 0
                    complete_num = len(complete_queryset.values())
                    defaults = {"score": score, "complete_num": complete_num, "num": num}
                    ActivityDailyData.objects.update_or_create(defaults=defaults, **kwargs)
                # study
                if act_type.study_type == 2:
                    study_queryset = EnterStudy.objects.filter(end_time__date=search_data, owner__in=user_list,
                                                               activity_id__in=act_list)
                    complete_num = len(study_queryset.values())
                    defaults = {"complete_num": complete_num, "num": complete_num}
                    ActivityDailyData.objects.update_or_create(defaults=defaults, **kwargs)


# 更新今日实际教学记录表（根据教师课程表）
def create_practical_course_record(time_range, klass_list=None):
    start_date = datetime.datetime.strptime(time_range[0], '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(time_range[1], '%Y-%m-%d').date()
    ret_data = []
    if not klass_list:
        klass_list = Klass.objects.all().values_list('id', flat=True)
    for i in range((end_date - start_date).days + 1):
        day = start_date + datetime.timedelta(days=i)
        week = day.isoweekday()

        for klass_id in klass_list:
            teacher_schedule_list = TeacherSchedule.objects.filter(klass=klass_id, week=week)
            for item in teacher_schedule_list:
                defaults = {'teacher': item.teacher, "time_range": item.time_range}
                kwargs = {'klass': item.klass, 'teaching_date': day, 'schedule': item.schedule}
                try:
                    obj, flag = PracticalCourseRecord.objects.get_or_create(defaults=defaults, **kwargs)
                except Exception as e:
                    logger.debug(e)
                    continue
                else:
                    if flag:
                        data = PracticalCourseRecordSerializer(obj).data
                        ret_data.append(data)
    return ret_data
