from django.db import models
from django.utils import timezone

class WebCache(models.Model):
    url = models.CharField(max_length=256, primary_key=True)
    encoding = models.CharField(max_length=16)
    content = models.TextField()
    created = models.DateTimeField('cache created')

    def is_expired(self, delta):
        now = timezone.now()
        return self.created + delta < now
