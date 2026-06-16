import requests

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import redirect
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ConfirmCode
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ConfirmSerializer,
    CustomTokenObtainPairSerializer,
)


User = get_user_model()


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            code = user.confirm_code.code

            return Response(
                {
                    "message": "User registered successfully. Confirm your account with the code.",
                    "email": user.email,
                    "confirm_code": code,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(
                request,
                username=email,
                password=password,
            )

            if user is None:
                return Response(
                    {"error": "Invalid email or password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not user.is_active:
                return Response(
                    {"error": "User is not confirmed."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "message": "Login successful.",
                    "token": token.key,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmAPIView(APIView):
    def post(self, request):
        serializer = ConfirmSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            code = serializer.validated_data["code"]

            try:
                user = User.objects.get(email=email)
                confirm_code = ConfirmCode.objects.get(user=user)
            except (User.DoesNotExist, ConfirmCode.DoesNotExist):
                return Response(
                    {"error": "User or code not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if confirm_code.code != code:
                return Response(
                    {"error": "Invalid confirmation code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.is_active = True
            user.save(update_fields=["is_active"])
            confirm_code.delete()

            return Response({"message": "User confirmed successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class GoogleLoginAPIView(APIView):
    def get(self, request):
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            "?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            "&scope=openid%20email%20profile"
        )

        return redirect(google_auth_url)


class GoogleCallbackAPIView(APIView):
    def get(self, request):
        code = request.GET.get("code")

        if not code:
            return Response(
                {"error": "Google authorization code is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            return Response(
                {"error": "Failed to get token from Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_response.json().get("access_token")

        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_info_response.status_code != 200:
            return Response(
                {"error": "Failed to get user info from Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_info = user_info_response.json()

        email = user_info.get("email")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")

        if not email:
            return Response(
                {"error": "Google account email is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "registration_source": "google",
            },
        )

        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.registration_source = "google"

        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Google login successful.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )