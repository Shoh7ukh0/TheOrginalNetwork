from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'user1', 'user2', 'updated_on', 'room_group_name']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user1'] = instance.user1.username
        representation['user2'] = instance.user2.username
        return representation


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_session', 'user', 'message_detail']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation