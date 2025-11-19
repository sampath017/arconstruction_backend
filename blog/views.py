
from rest_framework import viewsets, permissions
from .models import Post
from .serializers import PostListSerializer, PostDetailSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    lookup_field = 'slug'
    filterset_fields = ['published_at', 'is_published']
    search_fields = ['title', 'excerpt', 'body']
    ordering_fields = ['published_at', 'title']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(is_published=True)

    def get_serializer_class(self):
        return PostDetailSerializer if self.action in ['retrieve', 'create', 'update', 'partial_update'] else PostListSerializer
