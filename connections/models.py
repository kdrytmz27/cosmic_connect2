# Dosya: connections/models.py
from django.db import models
from django.conf import settings

class Like(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes_given', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} likes {self.to_user}"