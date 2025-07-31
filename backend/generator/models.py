from django.db import models
from django.conf import settings

class GeneratedAsset(models.Model):
    ASSET_TYPE_CHOICES = (
        ("email", "Email"),
        ("checklist", "Checklist"),
        ("sms", "SMS"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    prompt_used = models.TextField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.asset_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
