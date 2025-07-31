from django.contrib import admin
from .models import Subscription, UsageRecord

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "is_active", "current_period_end")

@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "credits_used", "timestamp")
