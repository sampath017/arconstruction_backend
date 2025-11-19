
from django.contrib import admin
from .models import SiteInfo, StaticPage

@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ("company_name", "phone_primary", "email", "updated_at")

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "updated_at")
    search_fields = ("title", "body")
