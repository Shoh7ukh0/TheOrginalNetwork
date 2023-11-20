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
    path('user-follow/', views.UserFollowView.as_view(), name='user_follow'),
]
