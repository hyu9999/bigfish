from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from rest_auth.views import LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from rest_framework_swagger.views import get_swagger_view

from bigfish.apps.auth.views import SSOAuthView, BigfishLoginView, LoginExamine, GetServerTime, HFLoginView
from bigfish.apps.users.views import AuthUserViewSet, AuthUserCourseView, SNRegisterView
from bigfish.utils.views import upload_file, ci
from simple_sso.sso_client.client import Client

test_client = Client(settings.SSO_SERVER, settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY)

urlpatterns = [
    url(r'^ajax_select/', include(ajax_select_urls)),
    # admin
    url(r'^admin/', admin.site.urls),
    # sso
    url(r'^api/client/', include(test_client.get_urls())),
    url(r'^api/client/sso_auth/$', SSOAuthView.as_view(), name="sso_auth"),
    # auth
    url(r'^api/auth/examine/', LoginExamine.as_view(), name='examine'),
    url(r'^api/auth/login/', BigfishLoginView.as_view(), name='rest_login'),
    url(r'^api/auth/hf_login/', HFLoginView.as_view(), name='hf_login'),
    url(r'^api/auth/logout/', LogoutView.as_view(), name='rest_logout'),
    url(r'^api/auth/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    url(r'^api/auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    url(r'^api/auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    url(r'^api/auth/user/', AuthUserViewSet.as_view(), name='rest_user_details'),
    url(r'^api/auth/user_course/', AuthUserCourseView.as_view(), name='rest_user_course'),
    # url(r'^api/auth/registration/', include('rest_auth.registration.urls')),
    url(r'^api/auth/sn_register/', SNRegisterView.as_view(), name='sn_register'),
    url(r'^api/auth/get_server_time/', GetServerTime.as_view(), name='get_server_time'),
    # bigfish app urls
    url(r'^api/achievement/', include('bigfish.apps.achievement.urls')),
    url(r'^api/area/', include('bigfish.apps.areas.urls')),
    url(r'^api/attention/', include('bigfish.apps.attention.urls')),
    url(r'^api/classroom/', include('bigfish.apps.classrooms.urls')),
    url(r'^api/collection/', include('bigfish.apps.collection.urls')),
    url(r'^api/contents/', include('bigfish.apps.contents.urls')),
    url(r'^api/dubbing/', include('bigfish.apps.dubbing.urls')),
    url(r'^api/homework/', include('bigfish.apps.homework.urls')),
    url(r'^api/integral/', include('bigfish.apps.integral.urls')),
    url(r'^api/intelligentpush/', include('bigfish.apps.intelligentpush.urls')),
    url(r'^api/knowledgepoint/', include('bigfish.apps.knowledgepoint.urls')),
    url(r'^api/public/', include('bigfish.apps.operation.urls')),
    url(r'^api/operation/', include('bigfish.apps.public.urls')),
    url(r'^api/questions/', include('bigfish.apps.questions.urls')),
    url(r'^api/reports/', include('bigfish.apps.reports.urls')),
    url(r'^api/research/', include('bigfish.apps.research.urls')),
    url(r'^api/textbooks/', include('bigfish.apps.textbooks.urls')),
    url(r'^api/resources/', include('bigfish.apps.resources.urls')),
    url(r'^api/schools/', include('bigfish.apps.schools.urls')),
    url(r'^api/shop/', include('bigfish.apps.shops.urls')),
    url(r'^api/textbooks/', include('bigfish.apps.textbooks.urls')),
    url(r'^api/users/', include('bigfish.apps.users.urls')),
    url(r'^api/versionupdate/', include('bigfish.apps.versionupdate.urls')),
    url(r'^api/versus/', include('bigfish.apps.versus.urls')),
    url(r'^api/voice/', include('bigfish.apps.voice.urls')),
    # 希沃
    url(r'^api/xiwo/', include('bigfish.apps.xiwo.urls')),
    # superfish
    url(r'^api/impactassessment/', include('bigfish.apps.impactassessment.urls')),
    url(r'^api/overall/', include('bigfish.apps.overall.urls')),
    url(r'^api/teachingfeedback/', include('bigfish.apps.teachingfeedback.urls')),
    url(r'^api/versionupdate/', include('bigfish.apps.versionupdate.urls')),
    url(r'^upload_file/$', view=upload_file, name="upload_file"),
    url(r'^webhook/ci/$', view=ci, name="ci"),
    # wechat
    url(r'^api/bfwechat/', include('bigfish.apps.bfwechat.urls')),
    url(r'^MP_verify_nrJENWWPyqyvzzNX\.txt$', TemplateView.as_view(template_name='MP_verify_nrJENWWPyqyvzzNX.txt')),
    url(r'^bf_wechat/$', TemplateView.as_view(template_name='wechat/index.html')),
]
if settings.DEBUG:
    urlpatterns += [
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^api/docs/', get_swagger_view(title='Big Fish API')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_title = 'Big Fish BACKEND'
admin.site.site_header = 'Big Fish BACKEND'
# admin.site.__class__ = OTPAdminSite
