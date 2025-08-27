# billing/admin.py
from django.contrib import admin
from .models import Subscription, UsageRecord

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "trial_remaining", "top_up_credits", "is_active")
    list_filter = ("plan", "is_active")
    search_fields = ("user__email", "user__username")

@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "credits_used", "timestamp")
    search_fields = ("user__email", "user__username")
