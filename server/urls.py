from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get_all_server/$', views.GetServerListView.as_view()),
    url(r'^get_all_healthcheck/$', views.GetServerHealthCheck.as_view()),
    url(r'^get_schedule_all_healthcheck/$', views.GetScheduleServerHealthCheck.as_view()),
    url(r'^register/$', views.ServerRegister.as_view()),
    url(r'^update/$', views.ServerUpdateView.as_view()),
    url(r'^delete/$', views.ServerDeleteView.as_view()),
]
