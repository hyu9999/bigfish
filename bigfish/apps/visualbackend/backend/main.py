import datetime
import multiprocessing

from bigfish.apps.impactassessment.backend.main import impact_assessment_main
from bigfish.apps.overall.backend.main import overall_main
from bigfish.apps.teachingfeedback.backend.main import teaching_feedback_main
from bigfish.apps.visualbackend.backend.commons import get_klass_list, get_current_term, get_current_week
from bigfish.apps.visualbackend.backend.studentdata import write_to_student_data
from bigfish.apps.visualbackend.backend.teacherdata import write_to_teacher_data


def main_func():
    current_time = datetime.datetime.now()
    term = get_current_term(current_time)
    if not term:
        print("获取学期信息失败")
        exit(-1)
    klass_list = get_klass_list()
    pool = multiprocessing.Pool(processes=2)
    # 收集用户基础数据
    pool.apply_async(write_to_student_data, (term,))
    pool.apply_async(write_to_teacher_data, (term,))
    pool.close()
    pool.join()
    # overall 总体情况
    overall_main(term, klass_list)
    # teaching feedback 教学反馈情况
    teaching_feedback_main(term, klass_list)
    # impact assessment 月度，学周 数据
    week = get_current_week(current_time)
    if not week:
        print("获取学周失败")
        exit(-2)
    impact_assessment_main(week, current_time)


if __name__ == '__main__':
    main_func()
