from ast import List
from django.urls import path, re_path, include
from django.contrib import admin
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth.models import AbstractBaseUser


UserModel = get_user_model()


class UsersListView(LoginRequiredMixin, ListView):
    http_method_names = ['get', ]

    def get_queryset(self):
        return UserModel.objects.all().exclude(id=self.request.user.id)

    def render_to_response(self, context, **response_kwargs):
        users: List[AbstractBaseUser] = context['object_list']

        data = [{
            "username": user.get_username(),
            "pk": str(user.pk)
        } for user in users]
        return JsonResponse(data, safe=False, **response_kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('original/', include(('original.urls', 'core',), namespace='core')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('users/', UsersListView.as_view(), name='users_list'),
    path('core/', include('core.urls')),
    
    path('api_auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)