from django.apps import AppConfig


class ContentMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feedback'
    verbose_name = 'Feedback app'
    verbose_name_plural = 'Feedback apps'