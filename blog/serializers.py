
from rest_framework import serializers
from .models import Post

class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'excerpt', 'cover_image', 'published_at']

class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'excerpt', 'body', 'cover_image', 'published_at']
