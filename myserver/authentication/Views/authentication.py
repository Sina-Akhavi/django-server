from authentication.Models.user import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        user = authenticate(username=user.username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username  = request.data.get('username')
        email     = request.data.get('email')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        
        if password1 != password2:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'User created successfully.', 'token': token.key}, status=status.HTTP_201_CREATED)

class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        profile_picture = request.FILES.get('profile_picture')
        phone_number = request.data.get('phone_number')
        city = request.data.get('city')
        country = request.data.get('country')

        if profile_picture:
            user.profile_picture = profile_picture
        if phone_number:
            user.phone_number = phone_number
        if city:
            user.city = city
        if country:
            user.country = country
        
        user.save()
        return Response({'message': 'User updated successfully.'}, status=status.HTTP_200_OK)
