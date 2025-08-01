from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    included_credits = models.PositiveIntegerField(default=0)
    top_up_credits = models.PositiveIntegerField(default=0)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    auto_top_up = models.BooleanField(default=False)  # ✅ user-controlled switch

    def get_total_credits(self):
        return self.included_credits + self.top_up_credits

    def consume_credit(self, amount=1):
        if self.top_up_credits >= amount:
            self.top_up_credits -= amount
        elif self.included_credits >= amount:
            self.included_credits -= amount
        else:
            raise ValueError("Insufficient credits")
        self.save()

    def should_auto_top_up(self):
        return self.auto_top_up and self.get_total_credits() <= 10

    def perform_auto_top_up(self):
        # TODO: call Stripe API to charge €5 and add 250 credits
        self.top_up_credits += 250
        self.save()


class UsageRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits_used = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.credits_used} credits"