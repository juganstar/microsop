from django.contrib import admin
from .models import GeneratedAsset

@admin.register(GeneratedAsset)
class GeneratedAssetAdmin(admin.ModelAdmin):
    list_display = ("user", "asset_type", "created_at")
    search_fields = ("user__email", "prompt_used")
    list_filter = ("asset_type", "created_at")
    ordering = ("-created_at",)
