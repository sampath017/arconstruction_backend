
from rest_framework import serializers
from .models import SiteInfo, StaticPage

class SiteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = '__all__'

class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['slug', 'title', 'body', 'updated_at']
