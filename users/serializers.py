import random
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ConfirmCode


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, username):
        if len(username) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return username

    def validate_password(self, password):
        if len(password) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return password

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_active=False
        )

        code = str(random.randint(100000, 999999))

        ConfirmCode.objects.create(
            user=user,
            code=code
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ConfirmSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField()

    def validate_code(self, code):
        if len(code) != 6:
            raise serializers.ValidationError("Code must contain 6 digits.")
        return code