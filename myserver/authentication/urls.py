
from django.urls import path, include
from authentication.Views.authentication import RegisterView, LoginView, CustomTokenRefreshView
from home.views import UpdateUserInfo

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/token/', CustomTokenRefreshView.as_view(), name='refresh-token'),
]
