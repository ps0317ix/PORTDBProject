from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers

from .models import TwitterSendContent


class TwitterSendContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TwitterSendContent
        fields = '__all__'

    def create(self, validated_data):
        return TwitterSendContent.objects.create(request_data=validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        else:
            instance = super().update(instance, validated_data)
        instance.save()
        return instance
