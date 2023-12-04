import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # ulanishni qabul qilish
        self.accept()
    
    def disconnect(self, close_code):
        pass

    # WebSocket dan xabar olish
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        messages = text_data_json['message']

        # WebSocket-ga xabar yuborish
        
        self.send(text_data=json.dumps({'message':message}))