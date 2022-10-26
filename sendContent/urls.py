from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get_all_send_content/$', views.TwitterSendContentListView.as_view()),
    url(r'^register/$', views.TwitterSendContentRegister.as_view()),
    url(r'^update/$', views.TwitterSendContentUpdateView.as_view())
]
