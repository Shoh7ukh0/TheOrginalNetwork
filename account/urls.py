from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/<str:username>/', views.ProfileView.as_view(), name='dashboard'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('user-list/', views.UserListView.as_view(), name='user_list'),
    path('user-detail/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/followers/<username>/', views.followers_list, name='user_followers'),
    path('users/follow/', views.user_follow, name='user_follow'),
]
