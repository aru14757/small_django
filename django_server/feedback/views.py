from rest_framework import viewsets
from .serializer import FeedbackSerializer
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Feedback

@csrf_exempt
def send_feedback_to_server(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Feedback.objects.create(
                telegram_id=data['telegram_id'],
                name=data['name'],
                message_type=data['message_type'],
                response=data['response'])

            return JsonResponse({'status': 'success'}, status=201)
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer