
from django.db import models
from django.utils.text import slugify

class Post(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True, max_length=180)
    excerpt = models.TextField(blank=True)
    body = models.TextField()  # Markdown or HTML
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published_at = models.DateTimeField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
