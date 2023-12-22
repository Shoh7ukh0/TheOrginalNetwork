from django.urls import path, include
from . import views

app_name = 'account'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.LoginView.as_view(), name='login'),
    path('dashboard/<str:username>/', views.ProfileView.as_view(), name='dashboard'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('user-list/', views.UserListView.as_view(), name='user_list'),
    path('user-detail/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user_follow/', views.UserFollowView.as_view(), name='user_follow'),

    # >>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<
    path('my_profile_about/', views.my_profile_about, name='my_profile_about'),
    path('my_profile_activity/', views.my_profile_activity, name='my_profile_activity'),
    path('my_profile_connections/', views.my_profile_connections, name='my_profile_connections'),
    path('my_profile_events/', views.my_profile_events, name='my_profile_events'),
    path('my_profile_media/', views.my_profile_media, name='my_profile_media'),
    path('my_profile_videos/', views.my_profile_videos, name='my_profile_videos'),
]
