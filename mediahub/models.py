
from django.db import models

class GalleryItem(models.Model):
    title = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to='images/')
    caption = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Image {self.pk}"
