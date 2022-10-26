from django.conf.urls import include, url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^allClient/$', views.GetClientListView.as_view()),
    url(r'^allLiver/$', views.GetLiverListView.as_view()),
    url(r'^popularLiver/$', views.GetPopularLiverListView.as_view()),
    url(r'^register/$', views.UserRegister.as_view()),
    url(r'^register_liver/$', views.LiverRegister.as_view()),
    path('register_liver_image1/<str:uuid>/', views.LiverImage1Register.as_view(), name='register_liver_image1'),
    path('register_liver_image2/<str:uuid>/', views.LiverImage2Register.as_view(), name='register_liver_image1'),
    path('register_liver_image3/<str:uuid>/', views.LiverImage3Register.as_view(), name='register_liver_image1'),
    url(r'^data/$', views.UserGetView.as_view()),
    url(r'^update/$', views.UserUpdateView.as_view()),
    url(r'^update_liver/$', views.LiverUpdateView.as_view()),
    url(r'^update_avatar/$', views.UserUpdateAvatarView.as_view()),
    url(r'^delete/$', views.UserDeleteView.as_view()),
]
