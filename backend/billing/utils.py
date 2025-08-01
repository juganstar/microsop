from datetime import datetime
from django.utils.timezone import now
from django.db import models  # ✅ Needed for models.Sum
from .models import UsageRecord

def get_credits_used_this_month(user):
    today = now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return UsageRecord.objects.filter(
        user=user, timestamp__gte=start_of_month
    ).aggregate(total=models.Sum("credits_used"))["total"] or 0

def get_monthly_limit_for_user(user):
    if not hasattr(user, "subscription"):
        return 0

    plan = user.subscription.plan
    if plan == "basic":
        return 10
    elif plan == "premium":
        return 50
    return 0
