from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get/$', views.ContactListView.as_view()),
    url(r'^register/$', views.ContactRegister.as_view()),
]
