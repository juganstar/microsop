# backend/generator/serializers.py
from rest_framework import serializers
from .models import GeneratedAsset

ALLOWED_TYPES = ("email", "checklist", "sms")
ALLOWED_TONES = ("professional", "friendly", "urgent", "casual")
ALLOWED_LANGS = ("en", "pt")


class GenerateRequestSerializer(serializers.Serializer):
    """Validates the POST body for GenerateSOPView before hitting the model."""
    prompt = serializers.CharField(min_length=5, max_length=4000)
    asset_type = serializers.ChoiceField(choices=ALLOWED_TYPES, default="email")
    language = serializers.ChoiceField(choices=ALLOWED_LANGS, default="en")
    tone = serializers.ChoiceField(choices=ALLOWED_TONES, default="professional")
    audience = serializers.CharField(required=False, allow_blank=True, max_length=200)
    constraints = serializers.CharField(required=False, allow_blank=True, max_length=400)
    brand_voice = serializers.CharField(required=False, allow_blank=True, max_length=200)
    include_signature = serializers.BooleanField(required=False, default=False)


class GeneratedAssetSerializer(serializers.ModelSerializer):
    """Read serializer for returning saved generations to the client."""
    # Optional tiny preview for listing UI
    preview = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedAsset
        fields = [
            "id",
            "asset_type",
            "prompt_used",
            "content",        # JSONField: email/checklist/sms schema
            "created_at",
            "preview",
        ]
        read_only_fields = ["id", "created_at"]

    def get_preview(self, obj):
        """
        Build a short human-friendly preview depending on asset_type.
        Safe against missing keys (just in case).
        """
        c = obj.content or {}
        if obj.asset_type == "email":
            subject = c.get("subject") or ""
            return (subject or "").strip()[:120]
        if obj.asset_type == "sms":
            msg = c.get("message") or ""
            return msg.strip()[:120]
        if obj.asset_type == "checklist":
            title = c.get("title") or "Checklist"
            count = len(c.get("items") or [])
            return f"{title} • {count} items"
        return ""
