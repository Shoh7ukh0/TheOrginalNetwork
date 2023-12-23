from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/like/', views.LikePostView.as_view(), name='like_post'),
    path('post/<int:post_id>/comment/', views.PostCommentView.as_view(), name='add_comment'),
    path('post/<int:post_id>/comment/<int:comment_id>/reply/', views.ReplyCommentView.as_view(), name='reply_comment'),
    path('post/<int:post_id>/comment/<int:comment_id>/like/', views.LikeCommentView.as_view(), name='like_comment'),
    path('<int:post_id>/edit/', views.EditPostView.as_view(), name='edit_post'),
    path('<int:post_id>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('search/', views.SearchUserView.as_view(), name='search_user'),
    path('post/<int:post_id>/hide/', views.HidePostView.as_view(), name='hide_post')
]