from .models import GalleryItem
from .serializers import GalleryItemSerializer
from .filters import GalleryFilterSet  # if you added the JSONField filter fix
from rest_framework import viewsets, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import json
from utils.tags import derive_tags
from .serializers import TAG_RULES


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Read for everyone; write for admin/staff only.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = GalleryItem.objects.filter(
        is_active=True).order_by("-created_at")
    serializer_class = GalleryItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    # If you added custom tags filter earlier, keep this:
    filterset_class = GalleryFilterSet
    search_fields = ["title", "caption"]
    ordering_fields = ["created_at", "title"]

    # Enable multipart/form-data for image uploads
    parser_classes = [parsers.MultiPartParser,
                      parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        qs = GalleryItem.objects.all()
        # Public users only see active items; admins see all for management
        if self.request.user and self.request.user.is_staff:
            return qs.order_by("-created_at")
        return qs.filter(is_active=True).order_by("-created_at")

    @action(detail=False, methods=["post"], permission_classes=[IsAdminOrReadOnly], url_path="bulk-upload")
    def bulk_upload(self, request):
        """
        Accepts multiple images under the same key 'images',
        plus optional shared fields, e.g., tags (JSON list), is_active, caption prefix, etc.
        """
        files = request.FILES.getlist("images")
        created = []
        errors = []

        # Optional shared metadata
        tags = request.data.get("tags")
        try:
            tags = json.loads(tags) if tags else []
        except Exception:
            tags = []

        # ...
        for f in files:
            base_title = request.data.get("title") or f.name
            provided_tags_raw = request.data.get(
                "tags")  # if client passed JSON string
            try:
                provided_tags = json.loads(
                    provided_tags_raw) if provided_tags_raw else []
            except Exception:
                provided_tags = []

            item = {
                "image": f,
                "title": base_title,
                "caption": request.data.get("caption", ""),
                "tags": provided_tags or derive_tags(base_title, TAG_RULES),
                "is_active": True,
            }
            # ...
            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                instance = serializer.save()
                created.append(instance.id)
            else:
                errors.append({f.name: serializer.errors})

        if errors:
            return Response({"created": created, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"created": created}, status=status.HTTP_201_CREATED)
