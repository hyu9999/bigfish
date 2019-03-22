import logging

from bigfish.utils.django.config_settings import config_django

config_django()
from django.contrib.auth.models import User
from rest_framework.utils import model_meta

logger = logging.getLogger('backend')

if __name__ == '__main__':
    # validated_data = {'address': '', 'textbook': '', 'fans_num': 0, 'registration_id': None, 'is_pilot_user': False,
    #                   'telephone': '', 'identity': '学生', 'first_login': True, 'lesson': 51, 'card_id': '0', 'icon': '',
    #                   'default_cid': '170', 'accumulate': 0, 'sex': '男生', 'default_grade': '小学一年级', 'level': 0,
    #                   'student_code': '0', 'nickname': 'test_attent001', 'default_class': '1', 'realname': '',
    #                   'coding': 0, 'attention_num': 0, 'province_code': '0',
    #                   "attend_class": [170, 172]}
    # info = model_meta.get_field_info(User)
    # many_to_many = {}
    # for field_name, relation_info in info.relations.items():
    #     print("-------", (field_name, relation_info))
    #     if relation_info.to_many and (field_name in validated_data):
    #         print("================================")
    #         many_to_many[field_name] = validated_data.pop(field_name)
    # print(many_to_many)
    tst_obj = User.objects.filter(profile__identity='老师', profile__attend_class__school_id=77).count()
    print(tst_obj)
    tst_obj = User.objects.filter(profile__identity='老师', profile__attend_class__id__in=[
        175,
        176,
        177,
        178,
        173,
        174]).distinct().count()
    print(tst_obj)
