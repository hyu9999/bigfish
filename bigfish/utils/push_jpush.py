import jpush
from collections import OrderedDict

from bigfish.settings.base import LOG_LEVEL
from bigfish.settings.dev import app_key, master_secret

_jpush = jpush.JPush(app_key, master_secret)
_jpush.set_logging(LOG_LEVEL)


class SendJPush(object):
    def __init__(self, send_type='message', platform=jpush.all_):
        self.push = _jpush.create_push()
        self.push.platform = platform
        self.send_type = send_type

    def run_send(self, audience):
        self.push.audience = audience
        try:
            self.push.send()
        except jpush.common.Unauthorized:
            raise jpush.common.Unauthorized("Unauthorized")
        except jpush.common.APIConnectionException:
            raise jpush.common.APIConnectionException("conn")
        except jpush.common.JPushFailure:
            print("JPushFailure")
        except:
            print("Exception")

    def send_message(self, send_msg, audience):
        self.push.message = jpush.message(send_msg)
        self.run_send(audience)

    def send_notification(self, send_msg, audience):
        self.push.notification = jpush.notification(alert=send_msg)
        self.run_send(audience)

    def send_by_type(self, send_msg, audience):
        if self.send_type == "message":
            self.send_message(send_msg, audience)
        elif self.send_type == "notification":
            self.send_notification(send_msg, audience)

    def push_to_all(self, send_msg):
        audience = jpush.all_
        self.send_by_type(send_msg, audience)

    def push_by_alias(self, send_msg, *args, **kwargs):
        audience = jpush.audience(jpush.tag(*args), **kwargs)
        self.send_by_type(send_msg, audience)

    def push_by_registration_id(self, send_msg, *args, **kwargs):
        audience = jpush.audience(jpush.registration_id(*args), **kwargs)
        self.send_by_type(send_msg, audience)


def get_json_data(type_val, send_msg, user_id):
    my_json = {"type": type_val, "message": send_msg, "user": user_id}
    return my_json


def normal_send_message(send_msg, registration_id_list):
    _jpush = jpush.JPush(app_key, master_secret)
    push = _jpush.create_push()
    push.audience = jpush.audience(
        jpush.registration_id(*registration_id_list),
    )
    push.message = jpush.message(send_msg)
    push.platform = jpush.all_
    try:
        response = push.send()
    except jpush.common.Unauthorized:
        raise jpush.common.Unauthorized("Unauthorized")
    except jpush.common.APIConnectionException:
        raise jpush.common.APIConnectionException("conn error")
    except jpush.common.JPushFailure:
        print("JPushFailure")
    except:
        print("Exception")

def dict_sort(dict_name):
    dict_data = OrderedDict
    dict_data = OrderedDict(sorted(dict_name.items(), key=lambda x:x[1], reverse=True))
    # for key, value in list_data:
    #     dict_data[key] = value
    return dict_data


if __name__ == '__main__':
    # jpush_obj = SendJPush()
    # registration_id_list = ['100d855909430b5a3c1']
    # jpush_obj.push_by_registration_id("您的账号已在别处登录", *registration_id_list)
    # send_msg = get_json_data(1, "nihao")
    # registration_id_list = ['100d855909430b5a3c1']
    # normal_send_message(send_msg, registration_id_list)
    d = {'农陆雅': 0, '陆晓丹': 0, '农永浩': 0, '敖朝凤梁正国': 0, '苏亚繁': 9.82, '朱光粉': 0, '向紫云': 0, '杨智慧': 12.659, '代芝延': 0, '周兴宇': 0, '吴文馨': 0, '保薇': 0, '胡明刚': 0, '杨晓': 0, '李秀超': 0, '龚登杰': 0, '陆祖铭': 0, '王永英': 0, '王开薇': 0, '雷澄松': 0, '满明卓': 7.478, '何大富': 0, '王振杰': 0, '黄文堂': 0, '黄贵琴': 0, '陆显珍': 0, '徐兴友': 0, '廖明权': 0, '陆富熠': 0, '赵守科': 0, '沈涵彩': 0, '俞若希': 0, '敖朝廷': 0, '陆兴云': 0, '吴仙': 0, '敖朝龙': 0, '詹小慧': 0, '严欢': 0, '刘安富': 0, '陆晴': 0, '卢永杰': 0, '蒋祥旺': 0, '邓粉': 0}
    print(dict_sort(d))
    # d = {'b':1, 'a':2, 'c':100}

