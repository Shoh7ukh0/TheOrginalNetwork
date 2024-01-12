from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ChatSession, ChatMessage
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# @api_view(['GET'])
@permission_classes([IsAuthenticated])
class HomeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        unread_msg = ChatMessage.count_overall_unread_msg(request.user.id)

        data = {
            'unread_msg': unread_msg
        }

        return Response(data)

# @api_view(['GET'])
@permission_classes([IsAuthenticated])
class CreateFriendAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_1 = request.user

        if request.GET.get('id'):
            user2_id = request.GET.get('id')
            user_2 = get_object_or_404(User, id=user2_id)
            get_create = ChatSession.create_if_not_exists(user_1, user_2)
            if get_create:
                messages.add_message(request, messages.SUCCESS, f'{user_2.username} successfully added in your chat list!!')
            else:
                messages.add_message(request, messages.SUCCESS, f'{user_2.username} already added in your chat list!!')
            return HttpResponseRedirect('/api/create-friend')
        else:
            user_all_friends = ChatSession.objects.filter(Q(user1=user_1) | Q(user2=user_1))
            user_list = []
            for ch_session in user_all_friends:
                user_list.append(ch_session.user1.id)
                user_list.append(ch_session.user2.id)
            all_user = User.objects.exclude(Q(username=user_1.username) | Q(id__in=list(set(user_list))))
            return Response({'all_user': all_user})


# @api_view(['GET'])
@permission_classes([IsAuthenticated])
class FriendListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_inst = request.user
        user_all_friends = ChatSession.objects.filter(Q(user1=user_inst) | Q(user2=user_inst)).select_related('user1', 'user2').order_by('-updated_on')
        all_friends = []
        for ch_session in user_all_friends:
            user, user_inst = [ch_session.user2, ch_session.user1] if request.user.username == ch_session.user1.username else [ch_session.user1, ch_session.user2]
            un_read_msg_count = ChatMessage.objects.filter(chat_session=ch_session.id, message_detail__read=False).exclude(user=user_inst).count()
            data = {
                "user_name": user.username,
                "room_name": ch_session.room_group_name,
                "un_read_msg_count": un_read_msg_count,
                "user_id": user.id
            }
            all_friends.append(data)

        user_1 = request.user
        if request.GET.get('id'):
            user2_id = request.GET.get('id')
            user_2 = get_object_or_404(User, id=user2_id)
            get_create = ChatSession.create_if_not_exists(user_1, user_2)
            if get_create:
                messages.add_message(request, messages.SUCCESS, f'{user_2.username} successfully added in your chat list!!')
            else:
                messages.add_message(request, messages.SUCCESS, f'{user_2.username} already added in your chat list!!')
            return HttpResponseRedirect('/api/friend-list')
        else:
            user_all_friends = ChatSession.objects.filter(Q(user1=user_1) | Q(user2=user_1))
            user_list = []
            for ch_session in user_all_friends:
                user_list.append(ch_session.user1.id)
                user_list.append(ch_session.user2.id)
            all_user = User.objects.exclude(Q(username=user_1.username) | Q(id__in=list(set(user_list))))
            return Response({'user_list': all_friends, 'all_user': all_user})

# @api_view(['GET'])
@permission_classes([IsAuthenticated])
class StartChatAPIView(APIView):
    def get(self, request, room_name, *args, **kwargs):
        current_user = request.user
        try:
            check_user = ChatSession.objects.filter(Q(id=room_name[5:]) & (Q(user1=current_user) | Q(user2=current_user)))
        except Exception:
            return HttpResponse("Something went wrong!!!")
        
        if check_user.exists():
            chat_user_pair = check_user.first()
            opposite_user = chat_user_pair.user2 if chat_user_pair.user1.username == current_user.username else chat_user_pair.user1
            fetch_all_message = ChatMessage.objects.filter(chat_session__id=room_name[5:]).order_by('message_detail__timestamp')
            
            data = {
                'room_name': room_name,
                'opposite_user': opposite_user.username,
                'fetch_all_message': [{'user': message.user.username, 'message': message.message_detail} for message in fetch_all_message]
            }
            
            return Response(data)
        else:
            return Response({"detail": "You don't have permission to chat with this user."}, status=403)

# @api_view(['GET'])
@permission_classes([IsAuthenticated])
class GetLastMessageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get('room_id')
        qs = ChatMessage.objects.filter(chat_session__id=session_id).order_by('-message_detail__timestamp')[:10]
        
        # Assuming your ChatMessage model has a 'message' field
        last_messages = [{'user': message.user.username, 'message': message.message_detail} for message in qs]
        
        return Response(last_messages)