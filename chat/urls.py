from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'chatapp'

urlpatterns = [
    # path(r'api/v1/', include(router.urls)),

    path('chat/', login_required(TemplateView.as_view(template_name='base/index.html')), name='chat'),
]