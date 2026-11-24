from django.db import models

class CollectionEntry(models.Model):
    image = models.ImageField(upload_to='collection/')
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-pk']
