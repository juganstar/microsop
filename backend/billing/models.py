from django.db import models
from django.conf import settings

class Subscription(models.Model):
    PLAN_CHOICES = (
        ("basic", "Basic"),
        ("premium", "Premium"),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    is_active = models.BooleanField(default=True)
    current_period_end = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.plan}"

class UsageRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credits_used = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.credits_used} credits"
