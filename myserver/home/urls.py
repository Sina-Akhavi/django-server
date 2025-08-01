
from django.urls import path
from home.views import ForecastPricesByARIMA, ForecastPricesByLSTM, HomeView, GetUser, UpdateUserInfo

urlpatterns = [
    path('test/', HomeView.as_view(), name='register'),
    path('user/', GetUser.as_view(), name='get_user'),
    path('user/update-info/', UpdateUserInfo.as_view(), name='get_user'),
    path('model-forecast/arima/', ForecastPricesByARIMA.as_view(), name='arima-forecast'),
    path('model-forecast/lstm/', ForecastPricesByLSTM.as_view(), name='lstm-forecast'),
]
