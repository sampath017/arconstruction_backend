# quotes/filters.py
import django_filters
from .models import Quote


class QuoteFilter(django_filters.FilterSet):
    created_from = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="gte")
    created_to = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="lte")
    status = django_filters.CharFilter(
        field_name="status", lookup_expr="iexact")
    email = django_filters.CharFilter(
        field_name="email", lookup_expr="icontains")
    service = django_filters.CharFilter(
        field_name="service", lookup_expr="icontains")
    assigned_to = django_filters.CharFilter(
        field_name="assigned_to", lookup_expr="icontains")
    tag = django_filters.CharFilter(method="filter_tag")

    def filter_tag(self, qs, name, value):
        return qs.filter(tags__contains=[value]) if value else qs

    class Meta:
        model = Quote
        fields = []
