from rest_framework import serializers, viewsets
from django.contrib.auth.models import User

from .models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'