from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from core.api import MessageModelViewSet, UserModelViewSet

app_name='chat'

router = DefaultRouter()
router.register(r'message', MessageModelViewSet, basename='message-api')
router.register(r'user', UserModelViewSet, basename='user-api')

urlpatterns = [
    re_path(r'api/v1/', include(router.urls)),

    path('', login_required(TemplateView.as_view(template_name='core/messaging.html')), name='chat'),
]
