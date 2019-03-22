import json
import logging

import requests
from django.contrib.auth.models import User
from django.db.models import Count, F, Max, Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import list_route, api_view, permission_classes
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from wechatpy import parse_message, create_reply, WeChatClient
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.replies import ArticlesReply, ImageReply, VoiceReply
from wechatpy.utils import check_signature

from bigfish.apps.attention.models import AttentionCircle
from bigfish.apps.bfwechat.models import ActiveToken, MediaSource, KeyWord, SendMsg, TemplateMsgRecord, \
    TemplateMsg, WxUser, WxUserRelationship, Feedback, WxArticleMsg, WxArticleMsgRecord
from bigfish.apps.bfwechat.robot import get_oauth_obj, jsapi_signature
from bigfish.apps.bfwechat.serializers import ActiveTokenSerializer, MediaSourceSerializer, KeyWordSerializer, \
    SendMsgSerializer, TemplateMsgRecordSerializer, \
    TemplateMsgSerializer, WxUserSerializer, FeedbackSerializer, WxArticleMsgRecordSerializer, WxArticleMsgSerializer, \
    WxUserRelationshipSerializer
from bigfish.apps.dubbing.models import UserDubbing, DubbingZan, CompetitionRank
from bigfish.apps.dubbing.serializers import UserDubbingSerializer
from bigfish.apps.public.models import Public
from bigfish.apps.schools.models import Klass
from bigfish.apps.users.models import BigfishUser
from bigfish.apps.users.serializers import UserSerializer
from bigfish.base import viewsets, status
from bigfish.base.response import BFValidationError
from bigfish.base.ret_msg import rsp_msg_200, rsp_msg_400
from bigfish.settings.base import WECHAT_APPID, WECHAT_APPSECRET, WECHAT_TOKEN, WX_WECHAT_APPID, WX_WECHAT_APPSECRET
from bigfish.utils.check_environment import check_wechat_env
from bigfish.utils.functions import generate_num_wx_user, check_env_wx

logger = logging.getLogger("django")


class ActiveTokenViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = ActiveToken.objects.all()
    serializer_class = ActiveTokenSerializer


class MediaSourceViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a media source instance.
    list:
        Return all media source, ordered by most recently joined.
    create:
        Create a new media source.
    delete:
        Remove an existing media source.
    partial_update:
        Update one or more fields on an existing media source.
    update:
        Update a media source.
    """
    queryset = MediaSource.objects.all()
    serializer_class = MediaSourceSerializer


class KeyWordViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a wechat keyword instance.
    list:
        Return all wechat keyword, ordered by most recently joined.
    create:
        Create a new wechat keyword.
    delete:
        Remove an existing wechat keyword.
    partial_update:
        Update one or more fields on an existing wechat keyword.
    update:
        Update a wechat keyword.
    """
    queryset = KeyWord.objects.all()
    serializer_class = KeyWordSerializer
    permission_classes = (AllowAny,)

    @list_route(methods=["GET"])
    def get_wx_menu(self, request):
        """
        查询自定义菜单

        :param request: \n

        :return: \n
            {
              "message": "success",
              "data": {
                "menu": {
                  "button": [
                    {
                      "name": "趣味配音",
                      "sub_button": [
                        {
                          "name": "作品预览",
                          "type": "view",
                          "sub_button": [],
                          "url": "http://ukk8i5.natappfree.cc/api/bfwechat/"
                        },
                        {
                          "name": "配音大赛",
                          "type": "click",
                          "sub_button": [],
                          "key": "V1001_DUBBING"
                        }
                      ]
                    },
                    {
                      "name": "用户中心",
                      "sub_button": [
                        {
                          "name": "账号绑定",
                          "type": "view",
                          "sub_button": [],
                          "url": "http://ukk8i5.natappfree.cc/api/bfwechat/binding_user/"
                        },
                        {
                          "name": "意见反馈",
                          "type": "view",
                          "sub_button": [],
                          "url": "http://ukk8i5.natappfree.cc/api/bfwechat/user_extra/get_student_info/"
                        }
                      ]
                    }
                  ]
                }
              },
              "code": 200
            }
        """
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        ret_data = client.menu.get()
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)

    @list_route(methods=["POST"])
    def create_wx_menu(self, request):
        """
        创建自定义菜单

        :param request:\n
            {
                "menu_data":{
                    "button":[
                        {
                            "type":"click",
                            "name":"今日歌曲",
                            "key":"V1001_TODAY_MUSIC"
                        },
                        {
                            "type":"click",
                            "name":"歌手简介",
                            "key":"V1001_TODAY_SINGER"
                        },
                        {
                            "name":"菜单",
                            "sub_button":[
                                {
                                    "type":"view",
                                    "name":"搜索",
                                    "url":"http://www.soso.com/"
                                },
                                {
                                    "type":"view",
                                    "name":"视频",
                                    "url":"http://v.qq.com/"
                                },
                                {
                                    "type":"click",
                                    "name":"赞一下我们",
                                    "key":"V1001_GOOD"
                                }
                            ]
                        }
                    ]
                }
            }

        :return:\n
            {"errcode":0,"errmsg":"ok"}
            or
            {"errcode":40018,"errmsg":"invalid button name size"}
        """
        menu_data = request.data.get("menu_data")
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        ret_data = client.menu.create(menu_data)
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)

    @list_route(methods=["GET"])
    def delete_wx_menu(self, request):
        """
        删除自定义菜单

        :param request:\n

        :return:\n
            {"errcode":0,"errmsg":"ok"}
        """
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        ret_data = client.menu.delete()
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class SendMsgViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a basic message instance.
    list:
        Return all basic messages, ordered by most recently joined.
    create:
        Create a new basic message.
    delete:
        Remove an existing basic message.
    partial_update:
        Update one or more fields on an existing basic message.
    update:
        Update a basic message.
    """
    queryset = SendMsg.objects.all()
    serializer_class = SendMsgSerializer


class TemplateMsgViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a template instance.
    list:
        Return all templates, ordered by most recently joined.
    create:
        Create a new template.
    delete:
        Remove an existing template.
    partial_update:
        Update one or more fields on an existing template.
    update:
        Update a template.
    """
    queryset = TemplateMsg.objects.all()
    serializer_class = TemplateMsgSerializer


class TemplateMsgRecordViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a template record instance.
    list:
        Return all template records, ordered by most recently joined.
    create:
        Create a new template record.
    delete:
        Remove an existing template record.
    partial_update:
        Update one or more fields on an existing template record.
    update:
        Update a template record.
    """
    queryset = TemplateMsgRecord.objects.all()
    serializer_class = TemplateMsgRecordSerializer
    permission_classes = (AllowAny,)

    @list_route(methods=['POST'])
    def send_template(self, request):
        """
        发送模板消息

        :param request:\n
            {
                "openid":1,
                "template":{
                    "template_id":"oYgjh1CLhL4bMwZzyC8StkgIybtA",
                    "url": "xxxxxxxxx",
                    "mini_program":{},
                    "data":
                    {
                        "first": {
                            "value": "亲爱的小丸家长，小丸同学今天的作业如下："
                        },
                        "name": {
                            "value": "小丸"
                        },
                        "subject": {
                            "value": "语文"
                        },
                        "content": {
                            "value": "预习第5课的内容，学习书写本课生字"
                        },
                        "remark": {
                            "value": "点击查看详情"
                        }
                    }
                }
            }
        :return:\n
        """
        user_id = request.data.get('openid')
        template = request.data.get('template')
        template_id = template.get('template_id')
        data = template.get('data')
        url = template.get('url')
        mini_program = template.get('mini_program')
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        try:
            ret_msg = client.message.send_template(user_id, template_id, data, url=url, mini_program=mini_program)
        except Exception as e:
            raise BFValidationError("发送模板消息失败！【{}】".format(e))
        else:
            error_msg = ret_msg.get("errcode", None)
            if ret_msg.get("errcode") == 0:
                if_success = True
            else:
                if_success = False
            # 取标题
            try:
                tm = TemplateMsg.objects.get(template_id=template_id)
            except Exception as e:
                logger.exception(e)
                title = ""
            else:
                title = tm.title
            # kwargs = {"title": title, "data": data, "template_id": template_id, "message_id": ret_msg.get("msgid"),
            #           "url": url, "from_user": request.user.id, "to_user": user_id, "mini_program": mini_program,
            #           "if_success": if_success, "error_msg": error_msg}
            kwargs = {"title": title, "data": data, "template_id": template_id, "message_id": ret_msg.get("msgid"),
                      "url": url, "to_user": user_id, "mini_program": mini_program,
                      "if_success": if_success, "error_msg": error_msg}
            TemplateMsgRecord.objects.create(**kwargs)
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)


class WxArticleMsgViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a article instance.
    list:
        Return all article, ordered by most recently joined.
    create:
        Create a new article.
    delete:
        Remove an existing article.
    partial_update:
        Update one or more fields on an existing article.
    update:
        Update a article.
    """
    queryset = WxArticleMsg.objects.all()
    serializer_class = WxArticleMsgSerializer

    @list_route(methods=["POST"])
    def upload_image(self, request):
        """
        上传图文消息内的图片获取URL

        本接口所上传的图片不占用公众号的素材库中图片数量的5000个的限制。图片仅支持jpg/png格式，大小必须在1MB以下。
        :param request:\n
            {
                "title":"xxx",
                "media_file":"xxxx"
            }
        :return:\n
            {
                "url":  "http://mmbiz.qpic.cn/mmbiz/xcxcx"
            }
        """
        title = request.data.get("title")
        media_file = request.data.get("media_file")
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        try:
            ret_msg = client.media.upload_image(media_file)
        except Exception as e:
            raise BFValidationError("上传素材失败！【{}】".format(e))
        else:
            wx_url = ret_msg.get('url', None)
            if not wx_url:
                raise BFValidationError('上传素材失败！【{}】'.format(ret_msg))
            else:
                kwargs = {"title": title, "media_type": "image", "wx_url": wx_url}
                MediaSource.objects.create(**kwargs)
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def add_articles(self, request):
        """
        新增永久图文素材

        :param request: \n
            {
                "title":"xxx",
                "articles": [
                    {
                        "title": "xxx",
                        "thumb_media_id": "xxx", # 封面图片素材id(必须是永久的mediaID)
                        "author": "xxx",
                        "show_cover_pic": "xxx",
                        "content": "xxx",
                        "content_source_url": "xxx",
                        "digest": "xxx",
                        "need_open_comment": "",
                        "only_fans_can_comment":""
                    }
                ]
            }
        :return:\n
            {
                "type": "news",
                "media_id": "xxxxxxxxxxxxxxxxxxxx-ip",
                "created_at": 1472520611
            }

        """
        title = request.data.get("title")
        articles = request.data.get("articles")
        if len(articles) not in range(1, 11):
            raise BFValidationError("一个图文消息支持1到10条图文！")
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        try:
            ret_msg = client.material.add_articles(articles)
        except Exception as e:
            raise BFValidationError("上传图文信息失败！【{}】".format(e))
        else:
            media_id = ret_msg.get("media_id", None)
            if not media_id:
                raise BFValidationError("上传图文消息失败！【{}】".format(ret_msg))
            content = []
            for item in articles:
                tmp_dict = {
                    "title": item.get('title'),
                    "description": item.get('digest'),
                    "url": item.get('content_source_url'),
                    "picurl": "PIC_URL"
                }
                content.append(tmp_dict)
            kwargs = {"title": title, "media_id": media_id, "content": content, "receive_msg": ret_msg}
            WxArticleMsg.objects.create(**kwargs)
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)


class WxArticleMsgRecordViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a article record instance.
    list:
        Return all article records, ordered by most recently joined.
    create:
        Create a new article record.
    delete:
        Remove an existing article record.
    partial_update:
        Update one or more fields on an existing article record.
    update:
        Update a article record.
    """
    queryset = WxArticleMsgRecord.objects.all()
    serializer_class = WxArticleMsgRecordSerializer

    @list_route(methods=["POST"])
    def send_articles(self, request):
        """
        发送图文消息(单条发送)

        :param request:\n
            {
                "title":"title",
                "openid": "xxx",
                "articles": [
                    {
                        "title": "Happy Day",
                        "description": "Is Really A Happy Day",
                        "url": "http://grj69b.natappfree.cc/media/logo_small.png",
                        "picurl": "PIC_URL"
                    },
                    {
                        "title": "Happy Day",
                        "description": "Is Really A Happy Day",
                        "url": "http://grj69b.natappfree.cc/media/logo_small.png",
                        "picurl": "PIC_URL"
                    }
                ]
            }
        :return:
        """
        title = request.data.get("title")
        user_id = request.data.get("openid")
        articles = request.data.get("articles")
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        media_id = ""
        try:
            ret_msg = client.message.send_articles(user_id, articles)
        except Exception as e:
            raise BFValidationError("发送模板消息失败！【{}】".format(e))
        else:
            if not isinstance(articles, (tuple, list)):
                media_id = articles
                try:
                    articles = client.material.get(media_id).get("news_item")
                except Exception as e:
                    raise BFValidationError("获取图文信息失败！【{}】".format(e))
            kwargs = {"title": title, "media_id": media_id, "receiver": {"group_or_users": user_id},
                      "content": articles, "receive_msg": ret_msg}
            WxArticleMsgRecord.objects.create(**kwargs)
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)

    @list_route(methods=["POST"])
    def send_mass_article(self, request):
        """
        群发图文消息

        :param request:\n
            group_or_users : 值为整型数字时为按分组群发，值为列表/元组时为按 OpenID 列表群发
                            当 is_to_all 为 True 时，传入 None 即对所有用户发送。\n
            {
                "group_or_users": "xxx",
                "media_id": "xxx",
                "is_to_all": "xxx",
                "preview": "xxx"
            }
        :return:
        """
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        group_or_users = request.data.get("group_or_users")
        media_id = request.data.get("media_id")
        is_to_all = request.data.get("is_to_all")
        preview = request.data.get("preview")
        title = ""
        try:
            wx_am = WxArticleMsg.objects.get(media_id=media_id)
        except Exception as e:
            logger.exception(e)
            content = client.material.get(media_id).get("news_item")
        else:
            title = wx_am.title
            content = wx_am.content
        try:
            ret_msg = client.message.send_mass_article(group_or_users, media_id, is_to_all=is_to_all, preview=preview)
        except Exception as e:
            raise BFValidationError("发送模板消息失败！【{}】".format(e))
        else:
            kwargs = {"title": title, "media_id": media_id, "receiver": {"group_or_users": group_or_users},
                      "content": content, "receive_msg": ret_msg}
            WxArticleMsgRecord.objects.create(**kwargs)
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)


class WxUserViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a wechat user instance.
    list:
        Return all wechat users, ordered by most recently joined.
    create:
        Create a new wechat user.
    delete:
        Remove an existing wechat user.
    partial_update:
        Update one or more fields on an existing wechat user.
    update:
        Update a wechat user.
    """
    queryset = WxUser.objects.all()
    serializer_class = WxUserSerializer


class WxUserRelationshipViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a wechat user relationship instance.
    list:
        Return all wechat user relationship, ordered by most recently joined.
    create:
        Create a new wechat user relationship.
    delete:
        Remove an existing wechat user relationship.
    partial_update:
        Update one or more fields on an existing wechat user relationship.
    update:
        Update a wechat user relationship.
    """
    queryset = WxUserRelationship.objects.all()
    serializer_class = WxUserRelationshipSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a feedback instance.
    list:
        Return all feedback, ordered by most recently joined.
    create:
        Create a new feedback.
    delete:
        Remove an existing feedback.
    partial_update:
        Update one or more fields on an existing feedback.
    update:
        Update a feedback.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class CreateFeedbackView(CreateAPIView):
    """
        Create a new feedback.
    """
    permission_classes = (AllowAny,)
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    @check_wechat_env
    def post(self, request, *args, **kwargs):
        data = request.data
        unionid = data.get("unionid")
        try:
            WxUser.objects.get(id=unionid)
        except Exception as e:
            logger.debug(e)
            try:
                wx_user = WxUser.objects.get(unionid=unionid).id
            except Exception as e:
                raise BFValidationError("{}".format(e))
            else:
                data['wx_user'] = wx_user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(rsp_msg_200(serializer.data), status=status.HTTP_201_CREATED, headers=headers)


class GetStudentInfoView(GenericAPIView):
    """
    获取学生信息

    :param request:\n

            {
                "username": "xxxx"
            }

    :return:\n

            {
              "message": "success",
              "data": {
                "user_id": 679,
                "username": "1212902",
                "realname": "蜀大侠",
                "schools": "程序调试学校",
                "class": "小学一年级程序调试班级",
                "headimg": "xxxx",
                "followers_num": 0,
                "fans_num": 0
              },
              "code": 200
            }
    """
    permission_classes = (AllowAny,)
    queryset = BigfishUser.objects.all()
    serializer_class = UserSerializer

    @check_wechat_env
    def get(self, request):
        try:
            username = request.GET.get("username")
            queryset = BigfishUser.objects.get(user__username=username)
        except Exception as e:
            raise BFValidationError("{}".format(e))

        ret_data = {'user_id': queryset.user.id, 'realname': queryset.realname, "username": queryset.user.username,
                    'followers_num': queryset.attention_num, 'fans_num': queryset.fans_num, 'headimg': queryset.icon}
        try:
            klass_id = int(queryset.default_cid)
        except Exception as e:
            raise BFValidationError("查询用户班级错误![1.{}]".format(e))
        try:
            klass = Klass.objects.get(id=klass_id)
        except Exception as e:
            raise BFValidationError("查询用户班级错误![2.{}]".format(e))
        ret_data["class"] = "{}{}".format(klass.grade, klass.name)
        ret_data["school"] = klass.school.name
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class WechatLoginView(APIView):
    """
    微信登录接口

    :param request:\n

    :return:\n
        {
          "message": "success",
          "code": 200,
          "data": {
            "openid":"xzxzxzxzx",
            "timestamp": 1524743095,
            "nonceStr": "xxxxxxxxx",
            "appid": "xxxxxxxxxxxx",
            "signature": "xxxxxxxxxxxxxx",
            "unionid": "xxxxx",
            "url": "http://k5jkub.natappfree.cc/api/bfwechat/get_wx_basic_info/?code=011e"
          }
        }
    """
    permission_classes = (AllowAny,)

    @check_wechat_env
    def get(self, request):
        code = request.GET.get("code")
        oauth = get_oauth_obj(request)
        if not code:
            return redirect(oauth.authorize_url)
        try:
            ret_data = get_wx_basic(oauth, code)
        except Exception as e:
            raise BFValidationError("error![{}]".format(e))
        request.session["wx_basic"] = ret_data
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


def get_wx_basic(oauth, code):
    token_info = oauth.fetch_access_token(code)
    openid = token_info.get("openid")
    redirect_uri = oauth.authorize_url
    ret_data = {"appid": WECHAT_APPID, "url": redirect_uri, "openid": openid}
    sig_dict = jsapi_signature(redirect_uri)
    ret_data.update(sig_dict)
    client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
    user_info = client.user.get(openid)
    ret_data['unionid'] = user_info.get("unionid", None)
    return ret_data


class JsapiSignatureView(APIView):
    """
    获取 jsapi signature

    :param request: \n
        {
            "url":"xxxx"
        }
    :return:\n
        {
            "message": "success",
            "code": 200,
            "data": {
                "timestamp": 1525414016,
                "url": "xxxx",
                "signature": "45a82092b4d435b78601ebb5b8b712a642af2bfa",
                "noncestr": "0PCJwcja7pXOD4R"
            }
        }
    """
    permission_classes = (AllowAny,)

    @check_wechat_env
    def post(self, request):
        redirect_url = request.data.get('url')
        ret_dict = jsapi_signature(redirect_url)
        return Response(rsp_msg_200(ret_dict), status=status.HTTP_200_OK)


class AccessTokenDetailView(APIView):
    """
    获取access_token

    :param request: \n
    :return: \n
        {
            "data": {
                "access_token": "9_OlPUuyG8xbt-9woGC31Be8lKmO2SC1_LsOWGg1EQQCe_dQZbifCPKdHM_c_6CTpm8goB0naLHxyK8Z"
            },
            "message": "success",
            "code": 200
        }
    """
    permission_classes = (AllowAny,)

    @check_wechat_env
    def get(self, request):
        client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
        access_token = client.access_token
        ret_msg = {"access_token": access_token}
        return Response(rsp_msg_200(ret_msg), status=status.HTTP_200_OK)


class CreateBindUserView(CreateAPIView):
    """
    绑定用户

    :param request: \n
        {
            "username": "xxx",
            "unionid": "xxx"
        }

    :return: \n
        {
          "message": "success",
          "code": 200,
          "data": "绑定成功"
        }
    """
    permission_classes = (AllowAny,)
    queryset = WxUserRelationship.objects.all()
    serializer_class = WxUserRelationshipSerializer

    @check_wechat_env
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        unionid = request.data.get("unionid")
        openid = request.data.get("openid")
        is_active, obj = check_binding_relation(unionid, username)
        if is_active:
            return Response(rsp_msg_200("该用户已经绑定成功，无需再次绑定！"), status=status.HTTP_200_OK)
        # 用户存在，更新活跃状态
        if obj:
            obj.is_active = True
            obj.save()
            return Response(rsp_msg_200("绑定成功"), status=status.HTTP_200_OK)
        try:
            wxuser_obj = WxUser.objects.get(unionid=unionid)
        except Exception as e:
            # 获取微信用户信息
            wx_user_data = {"unionid": unionid, "password": "123456", "is_active": True}
            client = WeChatClient(WECHAT_APPID, WECHAT_APPSECRET)
            user_info = client.user.get(openid)
            # 写入微信用户数据
            wx_username = generate_num_wx_user(username)
            wx_user_data["username"] = wx_username
            wx_user_data["openid"] = openid
            wx_user_data["nickname"] = user_info.get("nickname")
            wx_user_data["sex"] = user_info.get("sex")
            wx_user_data["head_img"] = user_info.get("headimgurl")
            wx_user_data["area"] = {"country": user_info.get("country"), "province": user_info.get("province"),
                                    "city": user_info.get("city")}
            try:
                wxuser_obj = WxUser.objects.create(**wx_user_data)
            except Exception as e:
                raise BFValidationError("写入微信用户信息失败[{}]".format(e))

        # 写入微信关联表
        student = User.objects.get(username=username)
        try:
            WxUserRelationship.objects.create(wx_user=wxuser_obj, student=student)
        except Exception as e:
            raise BFValidationError("绑定用户失败[{}]".format(e))
        return Response(rsp_msg_200("绑定成功"), status=status.HTTP_200_OK)


class UnbindUserView(GenericAPIView):
    """
    解除绑定关系

    :param request: \n
        {
            "username": "xxx",
            "unionid": "xxx"
        }

    :return: \n
        {
          "message": "success",
          "code": 200,
          "data": "解绑成功"
        }
    """
    permission_classes = (AllowAny,)
    queryset = WxUserRelationship.objects.all()
    serializer_class = WxUserRelationshipSerializer

    @check_wechat_env
    def post(self, request):
        username = request.data.get("username")
        unionid = request.data.get("unionid")
        is_active, obj = check_binding_relation(unionid, username)
        if not is_active:
            return Response(rsp_msg_200("已为解绑状态，无需再次解绑！"), status=status.HTTP_200_OK)
        # 更新绑定状态
        obj.is_active = False
        obj.save()
        return Response(rsp_msg_200("解绑成功"), status=status.HTTP_200_OK)


def check_binding_relation(unionid, username):
    is_active, obj = True, None
    try:
        obj = WxUserRelationship.objects.get(wx_user__unionid=unionid, student__username=username)
    except Exception as e:
        logger.debug(e)
        flag = False
    else:
        flag = obj.is_active
    return flag, obj


class StudentDubbingListView(GenericAPIView):
    """
    学生配音作品列表

    :param request:

        username=xxx&is_competition=1

    :return:

        {

            "message": "success",

            "code": 200,

            "data": [

                {
                    "description": "test",
                    "create_time": "2018-05-02T10:28:57.107607",
                    "update_time": "2018-05-02T10:28:57.107607",
                    "video": null,
                    "audio": null,
                    "image": null,
                    "total_time": 11.0,
                    "user": 18,
                    "dubbingsrc": 1,
                    "is_public": true,
                    "area": 0,
                    "video_url": "",
                    "is_shared": false,
                    "stage": {},
                    "is_active": true,
                    "zan_num": 0,
                    "id": 1,
                    "user_name": "",
                    "user_icon": "",
                    "src_image": ""
                }

            ]

        }
    """
    permission_classes = (AllowAny,)
    queryset = UserDubbing.objects.all()
    serializer_class = UserDubbingSerializer

    @check_wechat_env
    def get(self, request):
        username = request.GET.get("username")
        is_competition = request.GET.get("is_competition", None)
        queryset = UserDubbing.objects.filter(user__username=username)
        if is_competition == "1":
            queryset = queryset.filter(is_competition=is_competition)
        user_dubbing = queryset.order_by('-create_time')

        ud_data = UserDubbingSerializer(user_dubbing, many=True).data
        return Response(rsp_msg_200(ud_data), status=status.HTTP_200_OK)


class BindUserListView(GenericAPIView):
    """
    绑定用户列表

    :param request:\n
        unionid=xxxx
    :return:\n
        {
            "message": "success",
            "code": 200,
            "data": [
                {
                "user_id": 679,
                "username": "1212902",
                "realname": "蜀大侠",
                "school": "程序调试学校",
                "class": "小学一年级程序调试班级",
                "headimg": "xxxx",
                "followers_num": 0,
                "fans_num": 0
                },
                {
                "user_id": 672,
                "username": "21323",
                "realname": "蜀大侠",
                "school": "程序调试学校",
                "class": "小学一年级程序调试班级",
                "headimg": "xxxx",
                "followers_num": 0,
                "fans_num": 0
                }
            ]
        }
    """
    permission_classes = (AllowAny,)
    queryset = WxUserRelationship.objects.all()
    serializer_class = WxUserRelationshipSerializer

    @check_wechat_env
    def get(self, request):
        unionid = request.GET.get("unionid")
        try:
            wx_user = WxUser.objects.get(unionid=unionid)
        except Exception as e:
            raise BFValidationError("未获取到微信用户信息！【{}】".format(e))
        queryset = WxUserRelationship.objects.filter(wx_user=wx_user, is_active=True).annotate(
            user_id=F('student__id'),
            username=F('student__username'),
            realname=F('student__profile__realname'),
            headimg=F('student__profile__icon'),
            class_id=F('student__profile__default_cid'),
        ).values("user_id", "username", "realname", "class_id", "headimg")
        ret_data = []
        for item in list(queryset):
            tmp_dict = {}
            tmp_dict.update(item)
            tmp_dict.pop("class_id", None)
            class_id = str(item.get("class_id"))
            try:
                klass = Klass.objects.get(id=class_id)
            except Exception as e:
                logger.exception(e)
                continue
            class_name = "{}{}".format(klass.grade, klass.name)
            tmp_dict["class"] = class_name
            school_name = klass.school.name
            tmp_dict["school"] = school_name
            followers_num = AttentionCircle.objects.filter(fans=tmp_dict.get('user_id')).aggregate(Count('user')).get(
                "user__count")
            fans_num = AttentionCircle.objects.filter(user=tmp_dict.get('user_id')).aggregate(Count('fans')).get(
                "fans__count")
            tmp_dict["followers_num"] = followers_num
            tmp_dict["fans_num"] = fans_num
            ret_data.append(tmp_dict)
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class DubbingZanUserListView(GenericAPIView):
    """
    获取作品最近点赞人(20人)

    :param request:

    userdubbing=xxx

    :return:
    """
    permission_classes = (AllowAny,)
    queryset = WxUserRelationship.objects.all()
    serializer_class = WxUserRelationshipSerializer

    @check_wechat_env
    def get(self, request):
        userdubbing = request.GET.get('userdubbing')
        queryset = DubbingZan.objects.filter(userdubbing=userdubbing)
        ret_data = queryset.values("user").annotate(Max("create_time")).annotate(
            user_id=F('user__id'),
            username=F('user__username'),
            realname=F('user__profile__realname'),
            nickname=F('user__profile__nickname'),
            icon=F('user__profile__icon'),
            create_time=F('create_time__max')
        ).values("user_id", "username", "realname", "nickname", "icon", "create_time").order_by("-create_time")[:20]
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class LatestDubbingListView(APIView):
    """
    获取用户最新的配音作品（2部）

    :param request:

    userdubbing=xxx&user=1

    :return:

    {
        "code": 200,
        "data": [
            {
                "create_time": "2018-05-02T15:16:58.707607",
                "user_id": 18,
                "is_active": true,
                "video": "",
                "update_time": "2018-05-02T15:16:58.707607",
                "video_url": "",
                "image": "",
                "total_time": 0.0,
                "id": 3,
                "stage": {},
                "audio": "",
                "area": 0,
                "description": "test",
                "dubbingsrc_id": 3,
                "is_shared": false,
                "is_public": true
            },
            {
                "create_time": "2018-05-02T11:47:44.434607",
                "user_id": 18,
                "is_active": true,
                "video": "",
                "update_time": "2018-05-02T11:48:04.917607",
                "video_url": "",
                "image": "",
                "total_time": 18.0,
                "id": 2,
                "stage": {},
                "audio": "",
                "area": 0,
                "description": "test11",
                "dubbingsrc_id": 2,
                "is_shared": false,
                "is_public": true
            }
        ],
        "message": "success"
    }
    """
    permission_classes = (AllowAny,)

    @check_wechat_env
    def get(self, request):
        userdubbing = request.GET.get('userdubbing')
        user = request.GET.get('user')
        queryset = UserDubbing.objects.filter(~Q(id=userdubbing), user=user)
        ret_data = queryset.values()
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


class DubbingCompetitionRankListView(APIView):
    """
    配音大赛排行榜

    :param request:\n
        # scope:area,schools,class,all
        {
            "user_id": 18,
            "competition":4,
            "scope":"area"
        }

    :return:\n
        {
            "message": "success",
            "code": 200,
            "data": {
                "rank_data": [
                    {
                        "id": 1,
                        "realname": "张三",
                        "rank": 1,
                        "headimg": "/media/headericon/tx_zm_M.png",
                        "username": "0001",
                        "works_id": 1,
                        "works_title": "test",
                        "user_id": 18,
                        "zan_num": 2
                    },
                    {
                        "id": 2,
                        "realname": "李四",
                        "rank": 2,
                        "headimg": "/media/headericon/tx_zm_M.png",
                        "username": "0002",
                        "works_id": 1,
                        "works_title": "test",
                        "user_id": 19,
                        "zan_num": 1
                    }
                ],
                "self_data": {
                    "id": 1,
                    "realname": "张三",
                    "rank": 1,
                    "headimg": "/media/headericon/tx_zm_M.png",
                    "username": "0001",
                    "works_id": 1,
                    "works_title": "test",
                    "user_id": 18,
                    "zan_num": 2
                }
            }
        }
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            raise BFValidationError("获取用户信息异常")
        competition = request.data.get("competition", None)
        if not competition:
            raise BFValidationError("请传入配音大赛id")
        scope = request.data.get("scope", None)
        # get rank data
        rank_data = get_competition_rank_data(competition, user_id, scope)
        for item in rank_data:
            try:
                DubbingZan.objects.get(user=user_id, userdubbing=item['works_id'])
                item['is_zan'] = True
            except Exception as e:
                logger.debug(e)
                item['is_zan'] = False
        # get self data
        self_query = [x for x in rank_data if x.get('user_id') == user_id]
        if len(self_query):
            self_data = self_query[0]
        else:
            self_data = {}
        ret_data = {"self_data": self_data, "rank_data": rank_data}
        return Response(rsp_msg_200(ret_data), status=status.HTTP_200_OK)


def get_competition_rank_data(competition, user_id, scope):
    base_queryset = CompetitionRank.objects.filter(competition=competition)
    if scope in ["area", "school", "class"]:
        try:
            owner_works = CompetitionRank.objects.get(competition=competition, user=user_id)
        except Exception as e:
            raise BFValidationError("查询用户作品失败【{}】".format(e))
        queryset = eval(
            "base_queryset.filter({0}_id=owner_works.{0}_id).order_by('rank', 'user_dubbing__create_time')".format(
                scope))
        rank_base_data = queryset.annotate(user_id=F('user__id'),
                                           username=F('user__username'),
                                           headimg=F('user__profile__icon'),
                                           works_id=F('user_dubbing__id'),
                                           works_title=F('user_dubbing__description')
                                           ).values(
            "id", "zan_num", "user_id", "username", "realname", "headimg", "works_id", "works_title").order_by("rank")
        rank_data = []
        for index, item in enumerate(list(rank_base_data)):
            rank = index + 1
            tmp_dict = {'rank': rank}
            tmp_dict.update(item)
            rank_data.append(tmp_dict)
    else:
        queryset = base_queryset.order_by('rank', 'user_dubbing__create_time')
        rank_data = queryset.annotate(user_id=F('user__id'),
                                      username=F('user__username'),
                                      headimg=F('user__profile__icon'),
                                      works_id=F('user_dubbing__id'),
                                      works_title=F('user_dubbing__description')).values(
            "id", "rank", "zan_num", "user_id", "username", "realname", "headimg", "works_id", "works_title")
        rank_data = list(rank_data)
    return rank_data


@csrf_exempt
def wechatpy_view(request):
    if request.method == 'GET':
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echo_str = request.GET.get('echostr', '')
        try:
            check_signature(WECHAT_TOKEN, signature, timestamp, nonce)
        except InvalidSignatureException:
            echo_str = 'error'
        response = HttpResponse(echo_str, content_type="text/plain")
        return response
    elif request.method == 'POST':
        ret_msg = ""
        msg = parse_message(request.body)
        kwargs = {"title": "{} 消息".format(msg.type), "msg_type": msg.type, "content": request.body}
        SendMsg.objects.create(**kwargs)
        if msg.type == "event" and msg.event == 'subscribe':
            public = Public.objects.get(title="wexin_subscribe")
            msg_type = public.content.get("msg_type", "text")
            message = public.content.get("message", "欢迎关注SuperFish!")
            if msg_type == 'image':
                reply = ImageReply(message=msg)
                reply.media_id = message
            elif msg_type == 'voice':
                reply = VoiceReply(message=msg)
                reply.media_id = message
            elif msg_type == 'article':
                reply = ArticlesReply(message=msg, articles=message)
            else:
                reply = create_reply(message, msg)
            response = HttpResponse(reply.render(), content_type="application/xml")
        else:
            try:
                message = KeyWord.objects.get(title=msg.content, content_type=msg.type).content
            except Exception as e:
                try:
                    public = Public.objects.get(title="wexin_default_reply")
                    message = public.content.get("message", "欢迎关注SuperFish!")
                except Exception as e:
                    message = ""
            reply = create_reply(message, msg)
            response = HttpResponse(reply.render(), content_type="application/xml")
        return response
    else:
        logger.info('--------------------------------')


@api_view(["GET"])
@permission_classes((AllowAny,))
@check_env_wx
def get_wxuser_children_info(request):
    unionid = request.GET.get('unionid', 0)
    # unionid = 'onALY0ePr6WDsWDTgoWcvDkYD7-Q'
    try:
        wx_obj = WxUser.objects.get(unionid=unionid)
    except Exception as e:
        logger.debug(e)
        return Response(rsp_msg_400('未查找到此ID用户！'), status=status.HTTP_200_OK)
    user_list = WxUserRelationship.objects.filter(wx_user=wx_obj, is_active=True).values_list('student', flat=True)
    data = []
    for user_id in user_list:
        try:
            user_obj = BigfishUser.objects.get(user=user_id)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400("请传入正确的用户id"), status=status.HTTP_200_OK)
        user_info = {'name': user_obj.realname, 'id': user_obj.user.id, 'icon': user_obj.icon}
        try:
            klass_obj = Klass.objects.get(id=user_obj.default_cid)
        except Exception as e:
            logger.debug(e)
            return Response(rsp_msg_400("用户默认班级id有误"), status=status.HTTP_200_OK)
        user_info['klass'] = klass_obj.get_grade_display() + klass_obj.name
        user_info['school'] = klass_obj.school.name
        data.append(user_info)
    return Response(rsp_msg_200(data), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@check_env_wx
def get_wxapp_userinfo(request):
    code = request.GET.get('code', None)
    if not code:
        return Response(rsp_msg_400('code为必传字段'), status=status.HTTP_200_OK)
    appid = WX_WECHAT_APPID
    secret = WX_WECHAT_APPSECRET
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'. \
        format(appid, secret, code)
    req = requests.get(url=url)
    data = str(req.content, encoding="utf-8")
    # data = {"message": "success", "data":{"unionid": "onALY0ePr6WDsWDTgoWcvDkYD7-Q",
    #                                     "openid":"ooLCt4rJo0yzqFt56YD2Ar5B5eAI",
    #                                     "session_key":"3hRVL6m0lsdALL0onl6zxQ=="},"code":200}
    data = json.loads(data)
    return Response(rsp_msg_200(data), status=status.HTTP_200_OK)
