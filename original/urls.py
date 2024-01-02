from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/like/', views.LikePostView.as_view(), name='like_post'),
    path('post/<slug:slug>/comment/', views.PostCommentView.as_view(), name='add_comment'),
    path('post/<slug:slug>/comment/<int:comment_id>/reply/', views.ReplyCommentView.as_view(), name='reply_comment'),
    path('post/<slug:slug>/comment/<int:comment_id>/like/', views.LikeCommentView.as_view(), name='like_comment'),
    path('<slug:slug>/edit/', views.EditPostView.as_view(), name='edit_post'),
    path('<slug:slug>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('hide_post/<slug:slug>/', views.HidePostView.as_view(), name='hide_post'),

    path('share_post/<slug:slug>/', views.share_post, name='share_post'),
]