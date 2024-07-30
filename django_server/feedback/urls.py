from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet, send_feedback_to_server

app_name = 'feedback'

router = DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet)

urlpatterns = [
    path('send_feedback/', send_feedback_to_server, name='send_feedback'),
    path('api/', include(router.urls)),
    path('docs/', include_docs_urls(title='Users API Documentation'))
]

