import datetime

from bigfish.apps.visualbackend.backend.commons import get_current_term, get_current_week, get_klass_list

from bigfish.apps.impactassessment.backend.KlassMonthData import write_to_klass_month_data
from bigfish.apps.impactassessment.backend.KlassWeekData import write_to_klass_week_data
from bigfish.apps.impactassessment.backend.studentdata import write_to_student_data


def impact_assessment_main(week, current_time):
    klass_list = get_klass_list()
    write_to_student_data(week, current_time)
    write_to_klass_week_data(week, klass_list)
    write_to_klass_month_data(week, klass_list, current_time)


if __name__ == '__main__':
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    w = get_current_week(ct)
    impact_assessment_main(w, ct)
