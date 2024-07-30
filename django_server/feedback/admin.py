from django.contrib import admin
from .models import Feedback



@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'name', 'message_type', 'response', 'time')
    list_filter = ('time',)


