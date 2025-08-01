from rest_framework import serializers
from generator.models import GeneratedAsset

class GeneratedAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedAsset
        fields = ["id", "asset_type", "prompt_used", "content", "created_at"]
