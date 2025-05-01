from django.urls import path, include
from authentication.Views.authentication import RegisterView, LoginView, CustomTokenRefreshView, PasswordResetRequestView, PasswordResetConfirmView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/token/', CustomTokenRefreshView.as_view(), name='refresh-token'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/confirmation/', PasswordResetConfirmView.as_view(), name='password-reset-confirmation'),
]
