from django.contrib import admin
from .models import Message
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm


admin.site.register(Message)