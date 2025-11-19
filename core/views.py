
from rest_framework import viewsets, mixins
from .models import SiteInfo, StaticPage
from .serializers import SiteInfoSerializer, StaticPageSerializer

class SiteInfoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SiteInfo.objects.all().order_by('-updated_at')[:1]
    serializer_class = SiteInfoSerializer

class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'
