from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    path('', views.LoginView.as_view(), name='login'),
    path('dashboard/<str:username>/', views.ProfileView.as_view(), name='dashboard'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('<str:username>/edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('user-list/', views.UserListView.as_view(), name='user_list'),
    path('user-detail/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user_follow/', views.UserFollowView.as_view(), name='user_follow'),

    # >>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<
    path('my_profile_about/', views.my_profile_about, name='my_profile_about'),
    path('my_profile_connections/', views.my_profile_connections, name='my_profile_connections'),

    path('save_post/', views.saved_posts, name='saved_posts'),
    path('save_post/<slug:slug>/', views.save_post, name='save_post'),
    path('delete_saved_post/<str:username>/<slug:slug>/', views.delete_saved_post, name='delete_saved_post'),

    path('help/', views.help, name='help'),
    path('help_details/', views.help_details, name='help_details'),
    path('privacy/', views.privacy, name='privacy'),

    # # url-адреса смены пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # url-адреса сброса пароля
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
