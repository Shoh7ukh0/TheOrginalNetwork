from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import ActiveUser
from .serializers import ActiveUserSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_chat(request):
    user = request.user
    try:
        active_user = ActiveUser.objects.get(user=user)
        active_user.is_chat_enabled = False
        active_user.save()
        return JsonResponse({'status': 'success', 'message': 'Chat disabled'})
    except ActiveUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found in chat'})
