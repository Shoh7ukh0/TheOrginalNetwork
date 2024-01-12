from django.urls import path
from .views import PostListView, EditPostAPIView, PostDetailView, PostCommentAPIView, \
            LikeCommentView, LikePostAPIView, DeletePostAPIView, ReplyCommentView, \
            HidePostAPIView, CopyLinkAPIView

app_name = 'core'

urlpatterns = [
    path('api/posts/', PostListView.as_view(), name='post_list_api'),
    path('api/posts/<slug:slug>/', EditPostAPIView.as_view(), name='edit_post_api'),
    path('api/posts/<slug:slug>/', PostDetailView.as_view(), name='api_post_detail'),
    path('api/post-comment/<slug:slug>/', PostCommentAPIView.as_view(), name='api_post_comment'),
    path('api/reply-comment/<slug:slug>/<int:comment_id>/', ReplyCommentView.as_view(), name='api_reply_comment'),
    path('api/like-comment/<int:comment_id>/', LikeCommentView.as_view(), name='api_like_comment'),
    path('api/like-post/<slug:slug>/', LikePostAPIView.as_view(), name='api_like_post'),
    path('api/delete-post/<slug:slug>/', DeletePostAPIView.as_view(), name='api_delete_post'),
    path('api/hide-post/<slug:slug>/', HidePostAPIView.as_view(), name='api_hide_post'),
    path('api/copy-link/<slug:slug>/', CopyLinkAPIView.as_view(), name='api_copy_link'),
]