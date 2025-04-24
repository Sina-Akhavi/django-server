from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({"detail": "Username, email, and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"detail": "Username and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "access": access_token,
            "refresh": refresh_token
        })


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
            
            user.save()
            
            return Response({"detail": "User information updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        
        
        
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]  # Make this accessible for everyone (no authentication needed)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            
            print(f"Refresh token received for user: {refresh['user_id']}")

            access_token = str(refresh.access_token)
            return Response({"access": access_token}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
    