from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('uuid', 'username', 'email', 'profile', 'password', 'is_active', 'is_staff', 'is_admin', 'date_joined', 'genre', 'hobby', 'line_id', 'message', 'image_1', 'image_2', 'image_3')

    def create(self, validated_data):
        return User.objects.create_user(request_data=validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        else:
            instance = super().update(instance, validated_data)
        instance.save()
        return instance


class LiverSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'uuid',
            'username',
            'email',
            'profile',
            'password',
            'is_active',
            'is_staff',
            'is_admin',
            'date_joined',
            'birthday',
            'genre',
            'hobby',
            'line_id',
            'start_live_date',
            'responsible_manager',
            'liver_kinds',
            'profession',
            'prefecture',
            'is_sent_dm_type',
            'live_app',
            'referral',
            'liver_id',
            'real_name',
            'sex',
            'message',
            'image_1',
            'image_2',
            'image_3'
        )

    def create(self, validated_data):
        try:
            serializer = User.objects.create_liver(request_data=validated_data)
            return serializer
        except Exception as e:
            print(type(e), e)
            return User.objects.create_liver(request_data=validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        else:
            instance = super().update(instance, validated_data)
        instance.save()
        return instance
