from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Post, SavedPost, Comment
from .forms import PostForm, CommentForm, SearchForm
from django.contrib.auth.models import User
import redis
from django.conf import settings
from datetime import datetime, timezone
from django.http import JsonResponse
from django.http import HttpResponseServerError
from account.models import Contact, Profile
from django.db.models import Q
from core.models import ChatSession, ChatMessage

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsOwner
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, CommentSerializer, SavedPostSerializer

# соединить с redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


@authentication_classes([])
@permission_classes([])
class PostListView(APIView):
    def get(self, request, tag_slug=None, *args, **kwargs):
        queryset = Profile.objects.filter(user_type=Profile.Status.BLOGER)
        current_url = request.build_absolute_uri()
        posts = Post.objects.filter(hidden=False).order_by('-created_at')
        user_post_count = Post.objects.filter(user=request.user).count()
        users = User.objects.filter(is_active=True)

        user = request.user
        friends = Contact.objects.filter(user_to=user)
        followers = Contact.objects.filter(user_from=user)
        
        for post in posts:
            time_difference = datetime.now(timezone.utc) - post.created_at
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            post.time_since_creation = f"{hours}h {minutes}m ago"

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

        serializer = PostSerializer(posts, many=True)

        context = {
            'posts': serializer.data,
            'queryset': queryset,
            'section': 'people', 
            'users': users, 
            'user_post_count': user_post_count, 
            'friends': friends, 
            'followers': followers,
            'current_url': current_url,
            'user_list': all_friends,
        }

        return Response(context)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES, instance=Post())  # Use instance=Post()
        if form.is_valid():
            post = form.save(commit=False)
            post.user = self.request.user  # Associate the post with the current user
            post.save()
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class EditPostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class PostDetailView(APIView):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        total_views = post.views + 1
        post.views = total_views
        post.save()

        serializer = PostSerializer(post)

        comments = post.comments.all()
        likes = post.likes.all()
        form = CommentForm()

        # Check if the image attribute has a value
        has_image = post.image.url if post.image else None

        # Check if the video attribute has a value
        has_video = post.video.url if post.video else None

        data = {
            'post': serializer.data,
            'comments': comments, 
            'likes': likes, 
            'form': form, 
            'has_image': has_image, 
            'has_video': has_video, 
            'total_views': total_views
        }

        return Response(serializer.data)

    @login_required
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('core:post_detail', slug=post.slug)
        comments = post.comments.all()
        likes = post.likes.all()

        # Check if the image attribute has a value
        has_image = post.image.url if post.image else None

        # Check if the video attribute has a value
        has_video = post.video.url if post.video else None

        data = {
            'post': serializer.data,
            'comments': comments, 
            'likes': likes, 
            'form': form, 
            'has_image': has_image, 
            'has_video': has_video,
        }

        return Response(serializer.data)


class PostCommentAPIView(APIView):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyCommentView(APIView):
    def get(self, request, slug, comment_id):
        post = get_object_or_404(Post, slug=slug)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data)

    def post(self, request, slug, comment_id):
        post = get_object_or_404(Post, slug=slug)
        parent_comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, user=request.user, reply_to=parent_comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeCommentView(APIView):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if user in comment.likes.all():
            # Foydalanuvchi allaqachon buni yoqtirgan bo'lsa, yo'qotib tashlash
            comment.likes.remove(user)
            liked = False
        else:
            # Foydalanuvchi yoqmasa, qo'shish
            comment.likes.add(user)
            liked = True

        return Response({'liked': liked})


class LikePostAPIView(APIView):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        return Response({'liked': liked})


@permission_classes([IsAuthenticated, IsOwner])  # Ruxsatni tekshirish decoratorini qo'shing
class DeletePostAPIView(APIView):
    def delete(self, request, slug):
        post = get_object_or_404(Post, slug=slug, user=request.user)
        post.comments.all().delete()
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@permission_classes([IsAuthenticated, IsOwner])  # Ruxsatni tekshirish decoratorini qo'shing
class HidePostAPIView(APIView):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, user=request.user)
        post.hidden = not post.hidden
        post.save()
        return Response({'message': 'Post hidden successfully'}, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
class CopyLinkAPIView(APIView):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, user=request.user)

        # Copy the link logic goes here
        # For simplicity, let's assume we just want to create a new post with the same content

        new_post_data = {
            'user': post.user,
            'title': post.title,
            'content': post.content,
            # Add other fields as needed
        }

        new_post_serializer = PostSerializer(data=new_post_data)

        if new_post_serializer.is_valid():
            new_post_serializer.save()
            return Response({'message': 'Link copied successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to copy link'}, status=status.HTTP_400_BAD_REQUEST)

# def share_post(request, slug):
#     post = get_object_or_404(Post, slug=slug)
#     share_url = request.build_absolute_uri(post.get_absolute_url())
#     return render(request, 'base/share_post.html', {'share_url': share_url})