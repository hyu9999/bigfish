import datetime
import logging
import multiprocessing

from bigfish.apps.visualbackend.backend.commons import get_current_term, get_klass_list

from bigfish.apps.teachingfeedback.backend.activitydata import write_to_activity_data
from bigfish.apps.teachingfeedback.backend.lessondata import write_to_lesson_data
from bigfish.apps.teachingfeedback.backend.testreview import write_to_test_review_data
from bigfish.apps.teachingfeedback.backend.unitdata import write_to_unit_data, write_to_unittest_data

logger = logging.getLogger('backend')


def teaching_feedback_main(term, klass_list):
    pool = multiprocessing.Pool(processes=5)
    result = [
        pool.apply_async(write_to_test_review_data, (term, klass_list)),
        pool.apply_async(write_to_unit_data, (term, klass_list)),
        pool.apply_async(write_to_unittest_data, (term, klass_list)),
        pool.apply_async(write_to_lesson_data, (term, klass_list)),
        pool.apply_async(write_to_activity_data, (term, klass_list)),
    ]
    pool.close()
    pool.join()
    for res in result:
        print(res.get())


if __name__ == '__main__':
    ct = datetime.datetime.now()
    t = get_current_term(ct)
    kl = get_klass_list()
    teaching_feedback_main(t, kl)
