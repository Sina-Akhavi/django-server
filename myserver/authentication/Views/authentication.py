from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from PIL import Image


class ObtainTokenView(APIView):
    permission_classes = [AllowAny]  # Anyone can access this (for login)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # If using email instead of username
        # Try to find user by email
        if "@" in username:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return Response({"detail": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Find user by username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"detail": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if password matches
        if user.check_password(password):
            # Generate JWT tokens (access and refresh)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Send tokens in response
            return Response({
                "access": access_token,
                "refresh": refresh_token
            })
        else:
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

