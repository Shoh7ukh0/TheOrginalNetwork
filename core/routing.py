from core import consumers

from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'^ws$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/call/<username>/', consumers.CallConsumer.as_asgi()),
    re_path(r'ws/call/<username>/<is_admin>/', consumers.CallConsumer.as_asgi()),
]
