from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token, verify_jwt_token)
from django.conf import settings  # 画像参照のため追加
from django.contrib.staticfiles.urls import static  # 画像参照のため追加
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # 画像参照のため追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', obtain_jwt_token),
    path('token-refresh/', refresh_jwt_token),
    path('token-verify/', verify_jwt_token),
    path('health/', include('health_check.urls')),
    path('api/user/', include('user.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/sender/', include('sender.urls')),
    path('api/send_content/', include('sendContent.urls')),
    path('api/send_dm/', include('sendDM.urls')),
    path('api/server/', include('server.urls')),
]

# urlpatterns += staticfiles_urlpatterns()
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
