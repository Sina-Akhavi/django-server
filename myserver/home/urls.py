
from django.urls import path
from home.views import HomeView, GetUser, UpdateUserInfo

urlpatterns = [
    path('test/', HomeView.as_view(), name='register'),
    path('user/', GetUser.as_view(), name='get_user'),
    path('user/update-info/', UpdateUserInfo.as_view(), name='get_user'),
]
