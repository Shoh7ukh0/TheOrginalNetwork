# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import MessageModel

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope["session"]["_auth_user_id"]
        self.group_name = "{}".format(user_id)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')

        if message_type == 'image':
            await self.handle_image_message(text_data_json)
        else:
            message = text_data_json.get('message', '')

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'recieve_group_message',
                    'message': message
                }
            )

    async def recieve_group_message(self, event):
        message = event['message']

        await self.send(
            text_data=json.dumps({
                'message': message
            })
        )

    async def handle_image_message(self, data):
        user_id = self.scope["session"]["_auth_user_id"]
        recipient_id = data.get('recipient', '')
        image_url = data.get('image_url', '')

        user = await self.get_user_by_id(user_id)
        recipient = await self.get_user_by_id(recipient_id)

        if user and recipient:
            # Save the image message to the database
            message = MessageModel.objects.create(
                user=user,
                recipient=recipient,
                body=image_url,  # Save the image URL as the message body
                message_type='image'
            )

            # Notify the recipient about the new image message
            await self.channel_layer.group_send(
                "{}".format(recipient.id),
                {
                    'type': 'image.message',
                    'message_id': message.id,
                    'timestamp': str(message.timestamp),
                    'user': user.username,
                    'body': message.body,
                    'message_type': message.message_type,
                }
            )

    async def image_message(self, event):
        message_id = event['message_id']
        timestamp = event['timestamp']
        user = event['user']
        body = event['body']
        message_type = event['message_type']

        await self.send(
            text_data=json.dumps({
                'type': 'image.message',
                'message_id': message_id,
                'timestamp': timestamp,
                'user': user,
                'body': body,
                'message_type': message_type,
            })
        )

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
