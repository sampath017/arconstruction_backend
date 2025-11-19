from rest_framework import serializers
from .models import Quote


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = [
            "id", "full_name", "email", "phone",
            "service", "description", "source_page",
            "status", "estimated_value", "contracted_value", "close_reason",
            "assigned_to", "tags", "notes",
            "attachment", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        # If setting status to 'won' but contracted_value missing, it’s fine for now,
        # but you can enforce rules here if you want stricter workflows.
        return attrs
