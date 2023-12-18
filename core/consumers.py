
# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from account.models import ActiveUser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope["session"]["_auth_user_id"]
        self.group_name = "{}".format(user_id)
        # Join room group

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None,bytes_data = None):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'recieve_group_message',
                'message': message
            }
        )

    async def recieve_group_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(
             text_data=json.dumps({
            'message': message
        }))

class CallConsumer(WebsocketConsumer):
    groups_info = {}
    def connect(self):
        self.accept()
        if self.scope['url_route']['kwargs'].get('is_admin', False):
            ActiveUser.objects.get_or_create(username=f"{self.scope['url_route']['kwargs']['username']}", is_admin=True)
            self.notify_other_users_disconnected()
        else:
            ActiveUser.objects.get_or_create(username=f"{self.scope['url_route']['kwargs']['username']}")
        # response to client, that we are connected.
        # active_admins = ActiveUser.objects.filter(is_admin=True).values_list('username', flat=True)
        active_admins = ActiveUser.objects.all().values_list('username', flat=True)
        self.send(text_data=json.dumps({
            'type': 'connection',
            'data': {
                'message': "Connected",
                'active_admins': list(active_admins),
                # 'active_admins': [] if self.scope['url_route']['kwargs'].get('is_admin', False) else list(active_admins),
            }
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.my_name,
            self.channel_name
        )
        ActiveUser.objects.filter(username=self.my_name).delete()
        self.notify_other_users_disconnected()
        
        
    # Receive message from client WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        eventType = text_data_json['type']

        if eventType == 'login':
            name = text_data_json['data']['name']

            # we will use this as room name as well
            self.my_name = name

            # Join room
            async_to_sync(self.channel_layer.group_add)(
                self.my_name,
                self.channel_name
            )
        
        if eventType == 'call':
            name = text_data_json['data']['name']
            print(self.my_name, "is calling", name);
 
            async_to_sync(self.channel_layer.group_send)(
                name,
                {
                    'type': 'call_received',
                    'data': {
                        'caller': self.my_name,
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )
        if eventType == 'extra_call':
            name = text_data_json['data']['name']
            print(self.my_name, "is calling", name);
 
            async_to_sync(self.channel_layer.group_send)(
                name,
                {
                    'type': 'extra_call_received',
                    'data': {
                        'caller': self.my_name,
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )

        if eventType == 'answer_call':
            caller = text_data_json['data']['caller']
            caller_room = self.scope['url_route']['kwargs']['username']

            async_to_sync(self.channel_layer.group_add)(caller_room, self.channel_name)
            async_to_sync(self.channel_layer.group_add)(caller, caller_room)

            async_to_sync(self.channel_layer.group_send)(
                caller,
                {
                    'type': 'call_answered',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )
            if CallConsumer.groups_info.get(caller, False) and not CallConsumer.groups_info[caller].get('third_user', False):
                CallConsumer.groups_info[caller]['third_user'] = {'username': caller_room, 'rtcMessage': text_data_json['data']['rtcMessage']}
                s_user_username = CallConsumer.groups_info[caller]['second_user']['username']
                s_user_rtc = CallConsumer.groups_info[caller]['second_user']['rtcMessage']

                async_to_sync(self.channel_layer.group_add)(caller_room, s_user_username)
                async_to_sync(self.channel_layer.group_add)(s_user_username, caller_room)

                async_to_sync(self.channel_layer.group_send)(
                    s_user_username,
                    {
                        'type': 'new_call',
                        'data': {
                            'to_user': caller_room
                        }
                    }
                )
                print('Third user worked')
            elif not self.groups_info.get(caller, False):
                CallConsumer.groups_info[caller] = {}
                CallConsumer.groups_info[caller]['second_user'] = {'username': caller_room, 'rtcMessage': text_data_json['data']['rtcMessage']}
                
        
        if eventType == 'extra_answer_call':
            caller = text_data_json['data']['caller']
            caller_room = self.scope['url_route']['kwargs']['username']

            async_to_sync(self.channel_layer.group_add)(caller_room, self.channel_name)
            async_to_sync(self.channel_layer.group_add)(caller, caller_room)

            async_to_sync(self.channel_layer.group_send)(
                caller,
                {
                    'type': 'extracall_answered',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )
            
        if eventType == 'ICEcandidate':

            user = text_data_json['data']['user']

            async_to_sync(self.channel_layer.group_send)(
                user,
                {
                    'type': 'ICEcandidate',
                    'data': {
                        'rtcMessage': text_data_json['data']['rtcMessage']
                    }
                }
            )
            
        if eventType == 'admin_connected':
            users = ActiveUser.objects.all()
            active_admins = users.filter(is_admin=True).values_list('username', flat=True)
            active_users = users.filter(is_admin=False).values_list('username', flat=True)
            for user in active_users:
                async_to_sync(self.channel_layer.group_send)(
                    user,
                    {
                        'type': 'admin_connected',
                        'data': {
                            'active_admins': list(active_admins)
                        }
                    }
                )
        if eventType == 'admin_disconnected':
            users = ActiveUser.objects.all()
            active_admins = users.filter(is_admin=True).values_list('username', flat=True)
            active_users = users.filter(is_admin=False).values_list('username', flat=True)
            for user in active_users:
                async_to_sync(self.channel_layer.group_send)(
                    user,
                    {
                        'type': 'admin_disconnected',
                        'data': {
                            'active_admins': list(active_admins)
                        }
                    }
                )
                

    def call_received(self, event):
        print('Call received by ', self.my_name )
        self.send(text_data=json.dumps({
            'type': 'call_received',
            'data': event['data']
        }))
        
    def extra_call_received(self, event):
        print('Call received by ', self.my_name )
        self.send(text_data=json.dumps({
            'type': 'extra_call_received',
            'data': event['data']
        }))
        
    def new_call(self, event):
        print('Call received by ', self.my_name )
        self.send(text_data=json.dumps({
            'type': 'new_call',
            'data': event['data']
        }))


    def call_answered(self, event):
        print(self.my_name, "'s call answered")
        self.send(text_data=json.dumps({
            'type': 'call_answered',
            'data': event['data']
        }))
    def extracall_answered(self, event):
        self.send(text_data=json.dumps({
            'type': 'call_answered',
            'data': event['data']
        }))

    def ICEcandidate(self, event):
        self.send(text_data=json.dumps({
            'type': 'ICEcandidate',
            'data': event['data']
        }))
        
    def admin_connected(self, event):
        self.send(text_data=json.dumps({
            'type': 'admin_connected',
            'data': event['data']
        }))
        
    def admin_disconnected(self, event):
        self.send(text_data=json.dumps({
            'type': 'admin_disconnected',
            'data': event['data']
        }))
    
    
    def notify_other_users_connected(self):
        users = ActiveUser.objects.all()
        active_admins = users.filter(is_admin=True).values_list('username', flat=True)
        active_users = users.filter(is_admin=False).values_list('username', flat=True)
        for user in active_users:
            async_to_sync(self.channel_layer.send)(
                user,
                {
                    'type': 'admin_connected',
                    'data': {
                        'active_admins': list(active_admins)
                    }
                }
            )

    def notify_other_users_disconnected(self):
        users = ActiveUser.objects.all()
        active_admins = users.filter(is_admin=True).values_list('username', flat=True)
        active_users = users.filter(is_admin=False).values_list('username', flat=True)
        for user in active_users:
            async_to_sync(self.channel_layer.group_send)(
                user,
                {
                    'type': 'admin_disconnected',
                    'data': {
                        'active_admins': list(active_admins)
                    }
                }
            )