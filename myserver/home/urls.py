
from django.urls import path
from home.views import HomeView

urlpatterns = [
    path('test/', HomeView.as_view(), name='register'),
]


