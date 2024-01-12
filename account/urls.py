from django.urls import path, include
from .views import SearchUserAPIView, ProfileAPIView, LoginAPIView, RegistrationAPIView, \
            EditProfileAPIView, MyProfileConnectionsAPIView, HelpView, PrivacyView, UserListAPIView, \
            DashboardAPIView, SavedPostsView, UserFollowAPIView, HelpDetailsView, SavePostView, \
            ProfileToPDFView, MyProfileAboutAPIView, UserDetailAPIView, NotificationsAPIView, DeleteSavedPostView

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('api/help/', HelpView.as_view(), name='api-help'),
    path('', LoginAPIView.as_view(), name='login-api'),
    path('api/privacy/', PrivacyView.as_view(), name='api-privacy'),
    path('api/user-list/', UserListAPIView.as_view(), name='user-list-api'),
    path('api/search/', SearchUserAPIView.as_view(), name='search-user-api'),
    path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard-api'),
    path('api/saved_posts/', SavedPostsView.as_view(), name='api-saved-posts'),
    path('api/user-follow/', UserFollowAPIView.as_view(), name='user-follow-api'),
    path('api/register/', RegistrationAPIView.as_view(), name='registration-api'),
    path('api/help-details/', HelpDetailsView.as_view(), name='api-help-details'),
    path('api/save_post/<slug:slug>/', SavePostView.as_view(), name='api-save-post'),
    path('api/edit-profile/', EditProfileAPIView.as_view(), name='edit-profile-api'),
    path('api/profile/<str:username>/', ProfileAPIView.as_view(), name='profile-api'),
    path('api/profile-to-pdf/', ProfileToPDFView.as_view(), name='api-profile-to-pdf'),
    path('api/my-profile-about/', MyProfileAboutAPIView.as_view(), name='my-profile-about-api'),
    path('api/user-detail/<str:username>/', UserDetailAPIView.as_view(), name='user-detail-api'),
    path('api/notifications/<str:username>/', NotificationsAPIView.as_view(), name='api-notifications'),
    path('api/my_profile_connections/', MyProfileConnectionsAPIView.as_view(), name='api-my-profile-connections'),
    path('api/delete_saved_post/<str:username>/<slug:slug>/', DeleteSavedPostView.as_view(), name='api-delete-saved-post'),


    # # url-адреса смены пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # url-адреса сброса пароля
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
