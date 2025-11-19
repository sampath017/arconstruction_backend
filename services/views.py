
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Service
from .serializers import ServiceListSerializer, ServiceDetailSerializer

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True).order_by('order')
    lookup_field = 'slug'

    def get_serializer_class(self):
        return ServiceDetailSerializer if self.action == 'retrieve' else ServiceListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = self.get_queryset()[:6]
        return Response(ServiceListSerializer(qs, many=True, context={'request': request}).data)
