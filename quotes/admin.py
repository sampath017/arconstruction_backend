from django.contrib import admin
from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "full_name", "email", "phone",
                    "service", "status", "estimated_value", "contracted_value")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone",
                     "service", "description", "notes")
    readonly_fields = ("created_at", "updated_at")
