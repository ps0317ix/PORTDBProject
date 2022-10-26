from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get_send_dm_list/$', views.GetTwitterSendListView.as_view()),
    url(r'^get_send_dm_cnt/$', views.GetTwitterSendDMCnt.as_view()),
    url(r'^is_send_dm_exe/$', views.IsTwitterSendExe.as_view()),
    url(r'^client_is_send_dm_exe/$', views.ClientIsTwitterSendExe.as_view()),
    url(r'^send_dm/$', views.TwitterSendDMMaster.as_view()),
    url(r'^get_send_dm_result/$', views.GetTwitterSendResultListView.as_view()),
    url(r'^update_send_dm_result/$', views.TwitterSendResultUpdateView.as_view())
]
