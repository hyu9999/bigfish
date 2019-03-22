import json
import sys

from bigfish.utils.django.config_settings import config_django

config_django()
from bigfish.apps.textbooks.backend.operate_json import simple_act_rule

from bigfish.apps.textbooks.models import Activity


def generate_data():
    """
    根据活动ID获取规则信息
    :param request: \n
        activity_id：1   #活动id
    :return: \n
    """
    queryset = Activity.objects.all().order_by('id')
    for act in queryset:
        print("{}*******************{}".format(act.id, act.rule))
        if not act.rule:
            continue
        try:
            ret_data = simple_act_rule(act.rule)
            ret_data = json.loads(json.dumps(ret_data))
            print("-------------{}".format(ret_data))
        except Exception as e:
            print(e)
            sys.exit(-1)
        else:
            try:
                act.rule_data = ret_data
                act.save()
            except Exception as e:
                print("{}=============================={}\n{}".format(act.id, e, ret_data))
                sys.exit(-2)


if __name__ == '__main__':
    generate_data()
