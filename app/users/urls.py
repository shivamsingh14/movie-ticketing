from django.conf.urls import url
from rest_framework.authtoken import views

from app.users.views import UserViewSet, UserLogoutView, ChangePasswordViewSet

urlpatterns = [
    url(r'^$', UserViewSet.as_view(
        {
            'post': 'create',
            'get': 'retrieve',
            'patch': 'partial_update'
        }
    ), name="users"),
    url(r'^change-password/', ChangePasswordViewSet.as_view({
        'patch': 'partial_update'
    }), name="user_change_password"),
    url(r'^login/$', views.ObtainAuthToken.as_view(), name="login"),
    url(r'logout/$', UserLogoutView.as_view(), name="logout"),
]
