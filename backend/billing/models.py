from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

PLAN_CHOICES = [
    ("free", "Free (unlimited)"),
    ("trial", "Trial (one-time bucket)"),
    ("basic", "Basic (100/mo)"),
    ("premium", "Premium (200/mo)"),
]

def period_start_default():
    return timezone.now()

def period_end_default():
    now = timezone.now()
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if first.month == 12:
        return first.replace(year=first.year + 1, month=1)
    return first.replace(month=first.month + 1)

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")

    # Admin-controlled plan; default to TRIAL for all new users
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="trial")
    trial_remaining = models.PositiveIntegerField(default=5)

    # Monthly buckets for paid
    included_credits = models.PositiveIntegerField(default=0)
    top_up_credits = models.PositiveIntegerField(default=0)

    # Stripe references
    stripe_customer_id = models.CharField(max_length=120, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=120, blank=True, default="")

    # Period tracking
    current_period_start = models.DateTimeField(default=period_start_default)
    current_period_end = models.DateTimeField(default=period_end_default)

    is_active = models.BooleanField(default=True)
    auto_top_up = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} • {self.plan}"

    def get_total_credits(self):
        return self.included_credits + self.top_up_credits

    def consume_credit(self, amount=1):
        if self.top_up_credits >= amount:
            self.top_up_credits -= amount
        elif self.included_credits >= amount:
            self.included_credits -= amount
        else:
            raise ValueError("Insufficient credits")
        self.save(update_fields=["included_credits", "top_up_credits"])

    def should_auto_top_up(self):
        return self.auto_top_up and self.get_total_credits() <= 10

    def perform_auto_top_up(self):
        self.top_up_credits += 100  # example top-up
        self.save(update_fields=["top_up_credits"])

class UsageRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits_used = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        email = getattr(self.user, "email", str(self.user))
        return f"{email} - {self.credits_used} credits"
