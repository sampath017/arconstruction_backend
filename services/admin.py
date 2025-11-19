
from django.contrib import admin
from .models import Service, ServiceFAQ

class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name", "short_description", "body")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceFAQInline]

@admin.register(ServiceFAQ)
class ServiceFAQAdmin(admin.ModelAdmin):
    list_display = ("service", "question", "order")
    search_fields = ("question", "answer")
