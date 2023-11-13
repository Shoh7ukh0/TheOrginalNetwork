from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('user-list/', views.UserListView.as_view(), name='user_list'),
    path('user-detail/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user-follow/', views.UserFollowView.as_view(), name='user_follow'),
]
