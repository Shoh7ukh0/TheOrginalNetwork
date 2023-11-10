from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    # post ko‘rilgan
    path('post-detail/', views.post_detail, name='post_detail'),
    path('comment/', views.post_comment, name='post_comment'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('search/', views.post_search, name='post_search'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('', views.home, name='home'),
    path('create/', views.create_post, name='create_post'),
]