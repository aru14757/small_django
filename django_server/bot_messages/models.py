from django.db import models
from django.utils.translation import gettext_lazy as _
ROLES_CHOICES = [
    ('supervisor', 'Supervisor'),
    ('mentor', 'Mentor'),
    ('shop', 'Shop'),
    ('security', 'Security'),
    ('office', 'Office'),
    ('support', 'Support'),
]

class Message(models.Model):
    role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    day = models.IntegerField(verbose_name=_('Дни'))
    message_kz = models.TextField()
    message_ru = models.TextField()
    time = models.TimeField()

    def __str__(self):
        return f"Message to {self.role} on day {self.day} at {self.time}"





