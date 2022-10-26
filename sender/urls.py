from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get_all_twitter_sender/$', views.TwitterSenderListView.as_view()),
    url(r'^get_twitter_sender_health_check/$', views.TwitterSenderHealthCheckListView.as_view()),
    url(r'^get_client_twitter_sender_health_check/$', views.TwitterSenderHealthCheckListView.as_view()),
    url(r'^register/$', views.TwitterSenderRegister.as_view()),
    url(r'^update/$', views.TwitterSenderUpdateView.as_view()),
    url(r'^delete/$', views.TwitterSenderDeleteView.as_view()),
    url(r'^get_list/$', views.TwitterGetListView.as_view()),
    url(r'^keyRegister/$', views.TwitterSenderKeyRegister.as_view())
]
