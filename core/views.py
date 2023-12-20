# chat/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import MessageModel
from .serializers import MessageSerializer

@method_decorator(csrf_exempt, name='dispatch')
class MessageApiView(View):
    def post(self, request, *args, **kwargs):
        recipient_username = request.POST.get('recipient', '')
        body = request.POST.get('body', '')
        message_type = request.POST.get('type', '')
        
        if message_type == 'image':
            image = request.FILES.get('image', None)
            if image:
                # Save the image message to the database
                recipient = User.objects.get(username=recipient_username)
                message = MessageModel.objects.create(
                    user=request.user,
                    recipient=recipient,
                    body=image.url,  # Save the image URL as the message body
                    message_type='image'
                )
                
                # Notify the recipient about the new image message
                self.notify_recipient(recipient.id, message.id, message.timestamp, request.user.username, message.body, message.message_type)
                
                return JsonResponse({'status': 'success', 'message': 'Image sent successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No image provided'})

        # Handle other types of messages here...

    def notify_recipient(self, recipient_id, message_id, timestamp, user, body, message_type):
        # Implement WebSocket notification to the recipient here...
        pass
