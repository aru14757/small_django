from datetime import timedelta
from django.db import models

class Manager(models.Model):
    LANGUAGE_CHOICES = {
        'kk': 'Kazakh',
        'ru': 'Russian',
    }
    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('mentor', 'Mentor'),
    ]

    telegram_id = models.IntegerField()
    language = models.CharField(max_length=2, default='kz', choices=LANGUAGE_CHOICES)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def employees(self):
        return Employee.objects.filter(models.Q(supervisor=self) | models.Q(mentor=self))


class Employee(models.Model):
    LANGUAGE_CHOICES = {
        'kk': 'Kazakh',
        'ru': 'Russian',
    }
    ROLE_CHOICES = [
        ('shop', 'Shop'),
        ('security', 'Security'),
        ('support', 'Support'),
        ('office', 'Office'),
    ]

    telegram_id = models.IntegerField()
    language = models.CharField(max_length=2, default='kz', choices=LANGUAGE_CHOICES)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    supervisor = models.ForeignKey(Manager, related_name='supervised_employees', limit_choices_to={'role': 'supervisor'},
                                   null=True, blank=True, on_delete=models.SET_NULL)
    mentor = models.ForeignKey(Manager, related_name='mentored_employees', limit_choices_to={'role': 'mentor'}, null=True,
                               blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_day = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.first_day:
            self.first_day = self.created_at + timedelta(days=1)
        super().save(*args, **kwargs)
