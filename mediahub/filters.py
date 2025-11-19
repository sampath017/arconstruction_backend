import django_filters
from django.db.models import Q
from .models import GalleryItem

class GalleryFilterSet(django_filters.FilterSet):
    # Comma-separated list: ?tags=renovation,shopfitting
    tags = django_filters.CharFilter(method='filter_tags', help_text="Comma-separated list of tags")

    def filter_tags(self, qs, name, value):
        """
        'Any' semantics: return items containing at least one requested tag.
        Uses Postgres JSON containment on arrays: tags__contains=[tag]
        """
        if not value:
            return qs
        requested = [t.strip() for t in value.split(',') if t.strip()]
        if not requested:
            return qs
        q = Q()
        for tag in requested:
            q |= Q(tags__contains=[tag])
        return qs.filter(q)

    class Meta:
        model = GalleryItem
        fields = []