from django.conf.urls import url
from rest_framework import routers

from bigfish.apps.homework.views import HomeWorkView, PushRecordView

router = routers.SimpleRouter()
router.register(r'homework', HomeWorkView)
router.register(r'pushrecord', PushRecordView)

urlpatterns = router.urls
# urlpatterns += (
#     url(r'^task_remind/$', views.TaskRemindView.as_view(), name="task_remind"),
#     url(r'^rank_list/$', views.RankListView.as_view(), name="rank_list"),
#     url(r'^score_overall/$', views.ScoreOverallView.as_view(), name="score_overall"),
#     url(r'^score_detail/$', views.ScoreDetailView.as_view(), name="score_detail"),
#     url(r'^task_detail/$', views.TaskDetailView.as_view(), name="task_detail"),
#     url(r'^format_term_list/$', views.FormatTermView.as_view(), name="format_term_list"),
# )
