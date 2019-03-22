from django.conf.urls import url
from rest_framework import routers

from bigfish.apps.bfwechat import views
from bigfish.apps.bfwechat.views import ActiveTokenViewSet, MediaSourceViewSet, KeyWordViewSet, SendMsgViewSet, \
    TemplateMsgViewSet, TemplateMsgRecordViewSet, WxUserViewSet, FeedbackViewSet, WxArticleMsgViewSet, \
    WxArticleMsgRecordViewSet

router = routers.SimpleRouter()
router.register(r'active_token', ActiveTokenViewSet)
router.register(r'media_source', MediaSourceViewSet)
router.register(r'keyword', KeyWordViewSet)
router.register(r'send_msg', SendMsgViewSet)
router.register(r'template_msg', TemplateMsgViewSet)
router.register(r'template_msg_record', TemplateMsgRecordViewSet)
router.register(r'wx_article_msg', WxArticleMsgViewSet)
router.register(r'wx_article_msg_record', WxArticleMsgRecordViewSet)
router.register(r'wx_user', WxUserViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = router.urls
urlpatterns += (
    url(r'^wechat_login/$', views.WechatLoginView.as_view(), name="wechat_login"),
    url(r'^jsapi_signature/$', views.JsapiSignatureView.as_view(), name="jsapi_signature"),
    url(r'^user_extra/get_student_info/$', views.GetStudentInfoView.as_view(), name="student_info"),
    url(r'^binding_user/$', views.CreateBindUserView.as_view(), name="binding_user"),
    url(r'^unbinding_user/$', views.UnbindUserView.as_view(), name="unbinding_user"),
    url(r'^student_dubbing_list/$', views.StudentDubbingListView.as_view(), name="student_dubbing_list"),
    url(r'^dubbing_zan_user_list/$', views.DubbingZanUserListView.as_view(), name="dubbing_zan_user_list"),
    url(r'^latest_dubbing_list/$', views.LatestDubbingListView.as_view(), name="latest_dubbing_list"),
    url(r'^dubbing_competition_rank_list/$', views.DubbingCompetitionRankListView.as_view(), name="dubbing_competition_rank_list"),
    url(r'^bind_user_list/$', views.BindUserListView.as_view(), name="bind_user_list"),
    url(r'^get_access_token/$', views.AccessTokenDetailView.as_view(), name="get_access_token"),
    url(r'^create_feedback/$', views.CreateFeedbackView.as_view(), name='create-feedback'),
    url(r'^get_wxuser_children_info/$', views.get_wxuser_children_info, name='get_wxuser_children_info'),
    url(r'^get_wxapp_userinfo/$', views.get_wxapp_userinfo, name='get_wxapp_userinfo'),
)
