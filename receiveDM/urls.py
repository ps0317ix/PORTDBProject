from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get_receive_dm_list/$', views.GetTwitterReceiveDMListView.as_view())
]
