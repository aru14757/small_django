from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, get_messages

app_name = 'bot_messages'

router = DefaultRouter()
router.register(r'managers', MessageViewSet)

urlpatterns = [
    path('get_messages/', get_messages, name='get_messages'),
    path('api/', include(router.urls)),
    path('docs/', include_docs_urls(title='Users API Documentation'))
]

