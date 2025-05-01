from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse  # optional for constructing URLs


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
            "refresh": refresh_token,
            "username": username
        })
        
          
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]  # Make this accessible for everyone (no authentication needed)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Prevent email enumeration by always returning success
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        
        token = default_token_generator.make_token(user)
        # Construct the URL for resetting the password. In a real app make sure this points to your frontend.
        reset_link = f"http://localhost:3000/reset-password?uid={user.pk}&token={token}"
        
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email="akhavi.sina.2001@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"detail": "If the email is registered, password reset instructions have been sent."},
                        status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        
        if not uid or not token or not new_password:
            return Response({"detail": "UID, token, and new password are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
