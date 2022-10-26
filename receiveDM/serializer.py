from rest_framework import serializers
from .models import TwitterReceiveDM


class TwitterReceiveDMSerializer(serializers.ModelSerializer):

    class Meta:
        model = TwitterReceiveDM
        fields = '__all__'

    def create(self, validated_data):
        return TwitterReceiveDM.objects.create(request_data=validated_data)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save()
        return instance
