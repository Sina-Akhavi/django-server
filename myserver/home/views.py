from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from home.services import UserSerializer
from rest_framework.response import Response
from rest_framework import status
import csv
import os
from django.conf import settings

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return HttpResponse('Hi Dear!!')

class GetUser(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            data = UserSerializer(user)  
            return Response(data.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateUserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            
            city = request.data.get('city')
            country = request.data.get('country')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            username = request.data.get('username')
            email = request.data.get('email')
            phone = request.data.get('phoneNumber')
            
            if city is not None:
                user.city = city
            if country is not None:
                user.country = country
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if username is not None:
                user.username = username
            if email is not None:
                user.email = email
            if phone is not None:
                user.phone_number = phone
            
            user.save()
            
            return Response({"detail": "User information updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    


class ForecastPricesByARIMA(APIView):
    # permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            forecast_days = int(request.query_params.get('forecast_days', 1))
            csv_path = settings.ARIMA_CSV_PATH
            rows = []
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader):
                    if i >= forecast_days:
                        break
                    row_with_index = {'index': i + 1}
                    row_with_index.update(row)
                    rows.append(row_with_index)
            return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ForecastPricesByLSTM(APIView):
    # permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            forecast_days = int(request.query_params.get('forecast_days', 1))
            csv_path = settings.LSTM_CSV_PATH
            rows = []
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader):
                    if i >= forecast_days:
                        break
                    row_with_index = {'index': i + 1}
                    row_with_index.update(row)
                    rows.append(row_with_index)
            return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)