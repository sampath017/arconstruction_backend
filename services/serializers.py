
from rest_framework import serializers
from .models import Service, ServiceFAQ

class ServiceFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFAQ
        fields = ['question', 'answer', 'order']

class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'slug', 'short_description', 'hero_image', 'order']

class ServiceDetailSerializer(serializers.ModelSerializer):
    faqs = ServiceFAQSerializer(many=True, read_only=True)
    class Meta:
        model = Service
        fields = ['name', 'slug', 'short_description', 'body', 'hero_image', 'faqs']
