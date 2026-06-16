import email

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ConfirmCode
from .serializers import RegisterSerializer, LoginSerializer, ConfirmSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            code = user.confirm_code.code

            return Response(
                {
                    'message': 'User registered successfully. Confirm your account with the code.',
                    'username': user.username,
                    'confirm_code': code
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=email, password=password)

            if user is None:
                return Response(
                    {'error': 'Invalid username or password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not user.is_active:
                return Response(
                    {'error': 'User is not confirmed.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    'message': 'Login successful.',
                    'token': token.key
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmAPIView(APIView):
    def post(self, request):
        serializer = ConfirmSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(username=username)
                confirm_code = ConfirmCode.objects.get(user=user)
            except:
                return Response(
                    {'error': 'User or code not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if confirm_code.code != code:
                return Response(
                    {'error': 'Invalid confirmation code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.is_active = True
            user.save()
            confirm_code.delete()

            return Response({'message': 'User confirmed successfully.'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer