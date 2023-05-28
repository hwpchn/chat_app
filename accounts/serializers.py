from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_auth.serializers import LoginSerializer as RestAuthLoginSerializer
from .models import FriendRequest


class CustomLoginSerializer(RestAuthLoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = get_user_model().objects.filter(email=email).first()

        if user and user.check_password(password):
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Invalid login credentials.')
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        email = validated_data.get('email')
        username = email.split('@')[0]  # take the part of the email before the @ as the username
        validated_data['username'] = username
        user = get_user_model().objects.create_user(**validated_data)
        return user


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'status')
