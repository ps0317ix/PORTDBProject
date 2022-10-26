from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers

from .models import TwitterSendDM


class TwitterSendDMSerializer(serializers.ModelSerializer):

    class Meta:
        model = TwitterSendDM
        fields = '__all__'

    def create(self, validated_data):
        return TwitterSendDM.objects.create(request_data=validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        else:
            instance = super().update(instance, validated_data)
        instance.save()
        return instance
