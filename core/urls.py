from django.urls import path
from .views import HomeAPIView, CreateFriendAPIView, FriendListAPIView, StartChatAPIView, GetLastMessageAPIView 

urlpatterns = [
    path('api/home/', HomeAPIView.as_view(), name='api_home'),     
    path('api/create-friend/', CreateFriendAPIView.as_view(), name='api_create_friend'),   
    path('api/friend-list/', FriendListAPIView.as_view(), name='api_friend_list'),    
    path('api/start-chat/<str:room_name>/', StartChatAPIView.as_view(), name='api_start_chat'),
    path('api/get-last-message/', GetLastMessageAPIView.as_view(), name='api_get_last_message'),
]