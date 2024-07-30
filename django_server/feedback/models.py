from django.db import models

class Feedback(models.Model):
    telegram_id = models.IntegerField()
    name = models.CharField(max_length=100)
    message_type = models.CharField(max_length=100)
    response = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"
    class Meta:
        ordering = ['id']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
