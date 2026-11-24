from django.db import models

class CollectionEntry(models.Model):
    image = models.ImageField(upload_to='collection/')
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-pk']


class Battle(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    turn_token = models.CharField(max_length=32)
    state = models.JSONField()
