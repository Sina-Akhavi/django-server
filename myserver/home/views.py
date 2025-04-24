from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from myserver.home.services import UserSerializer
from rest_framework.response import Response
from rest_framework import status

class HomeView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    
    def get(self, request):
        return HttpResponse('Hi Dear!!')

class GetUser(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    
    def get(self, request):
        try:
            user = request.user
            data = UserSerializer(user)  
            return Response(data.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    