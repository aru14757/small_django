from .models import Message
from rest_framework import viewsets
from .serializer import MessageSerializer
from django.http import JsonResponse
import json


def get_messages(request):
    if request.method == 'GET':
        try:
            messages = Message.objects.all()
            messages_list = list(
                messages.values('role', 'day', 'message_kz', 'message_ru', 'time'))
            return JsonResponse(messages_list, safe=False)

            return JsonResponse({'status': 'success'}, status=201)
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer