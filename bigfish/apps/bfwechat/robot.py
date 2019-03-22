import json
import re
from urllib import parse, request

import time
import wechatpy
import werobot
from django.core.cache import cache
from django.urls import reverse
from wechatpy import WeChatClient
from wechatpy.utils import random_string
from werobot import WeRoBot
from werobot.logger import logger

from bigfish.settings.base import WECHAT_TOKEN, WECHAT_APPID, WECHAT_APPSECRET

werobot.logger.enable_pretty_logging(logger, level='info')

robot = WeRoBot(enable_session=False,
                token=WECHAT_TOKEN,
                APP_ID=WECHAT_APPID,
                APP_SECRET=WECHAT_APPSECRET)


@robot.subscribe
def subscribe(message):
    """
    被关注时调用,返回信息给用户

    :param message:
    :return:
    """
    user_id = message.source
    templates = """
    Hi~尊敬的{}用户您好！\n感谢您关注“SuperFish智能英\n语”服务号！通过服务号您可以\n实时掌握自家孩子使用pad学习\n的情况！\n请进行“<font color="red">账号绑定</font>”后再进行讯息查询!
    """
    ret_msg = templates.format(user_id)
    return ret_msg


@robot.unsubscribe
def unsubscribe(message):
    """
    被取消关注时调用

    :param message:
    :return:
    """
    user_id = message.source


@robot.text
def handle_text(message):
    """
    处理文本信息

    :param message:
    :return:
    """
    msg = message.content.strip().lower()
    if re.compile("更新菜单").match(msg):
        try:
            create_menu_func()
        except Exception as e:
            return "create menu error[{}]".format(e)
        else:
            return "create menu success"
    elif re.compile("删除菜单").match(msg):
        try:
            robot.client.delete_menu()
        except Exception as e:
            return "delete menu error[{}]".format(e)
        else:
            return "delete menu success"
    else:
        return msg


def create_menu_func():
    """
    创建菜单

    :return:
    """
    client = robot.client
    data = {
        "button": [
            {
                "name": "趣味配音",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "作品预览",
                        "url": "http://ukk8i5.natappfree.cc/api/bfwechat/get_wx_basic_info/"
                    },
                    {
                        "type": "click",
                        "name": "配音大赛",
                        "key": "V1001_DUBBING"
                    }
                ]
            }, {
                "name": "用户中心",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "账号绑定",
                        "url": "https://flyingcloud.com.cn/api/bfwechat/wechat_login/"
                    },
                    {
                        "type": "view",
                        "name": "意见反馈",
                        "url": "http://ukk8i5.natappfree.cc/api/bfwechat/user_extra/get_student_info/?username=bianhongyu"
                    }
                ]
            },
        ]}
    try:
        client.create_menu(data)
    except Exception as e:
        logger.debug("create error[{}]".format(e))
    else:
        logger.debug("success")


def cache_value(key):
    result = cache.get(key)
    time = 60
    if not result:
        result = ""
        cache.set(key, result, time)
    return result


def check_env(req):
    user_agent = str(req.META.get("HTTP_USER_AGENT")).lower()
    if "micromessenger" in user_agent:
        return True
    else:
        return False


def get_oauth_obj(req):
    redirect_uri = "https://{}{}".format(req.get_host(), req.get_full_path())
    oauth = wechatpy.oauth.WeChatOAuth(WECHAT_APPID, WECHAT_APPSECRET, redirect_uri)
    return oauth


def wx_basic_view(req, namespace, callback_func, **params):
    flag = True
    if check_env(req):
        param_str = parse.urlencode(params)
        redirect_uri = "https://{}{}?{}".format(req.get_host(),
                                               reverse("{}:{}".format(namespace, callback_func)), param_str)
        state = random_string(length=15)
        auth_url = wechatpy.oauth.WeChatOAuth(WECHAT_APPID, WECHAT_APPSECRET, redirect_uri, state=state).authorize_url
        return flag, auth_url
    else:
        ret_msg = "请从微信端访问!"
        return flag, ret_msg


def fmt_url(url, **param_dict):
    param_dict = parse.urlencode(param_dict)
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
    req = request.Request(url="{}?{}".format(url, param_dict), headers=header_dict)
    res = request.urlopen(req)
    res = json.loads(res.read().decode())
    return res


def jsapi_signature(redirect_url):
    nonce_str = random_string(length=15)
    timestamp = int(time.time())

    client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
    ticket_response = client.jsapi.get_ticket()
    signature = client.jsapi.get_jsapi_signature(
        nonce_str,
        ticket_response['ticket'],
        timestamp,
        redirect_url
    )
    ret_dict = {
        'ticket': ticket_response['ticket'],
        'noncestr': nonce_str,
        'timestamp': timestamp,
        'url': redirect_url,
        'signature': signature
    }
    return ret_dict
