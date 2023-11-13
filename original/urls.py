from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('create/', views.CreatePostView.as_view(), name='create_post'),
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/like/', views.LikePostView.as_view(), name='like_post'),
    path('<int:post_id>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('<int:post_id>/edit/', views.EditPostView.as_view(), name='edit_post'),
    path('<int:post_id>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('search/', views.SearchUserView.as_view(), name='search_user'),
]