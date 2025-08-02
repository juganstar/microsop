from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from generator.openai_client import generate_micro_sop
from generator.models import GeneratedAsset
from generator.serializers import GeneratedAssetSerializer

from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user
from billing.models import UsageRecord

from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


CREDITS_PER_SOP = 1

@method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True), name='dispatch')
class GenerateSOPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        asset_type = request.data.get("asset_type", "micro_sop")

        if not prompt:
            return Response({"error": "Prompt is required."}, status=400)

        # Enforce monthly credit limit
        used_credits = get_credits_used_this_month(request.user)
        credit_limit = get_monthly_limit_for_user(request.user)

        if used_credits + CREDITS_PER_SOP > credit_limit:
            return Response({"error": "Credit limit reached for this month."}, status=403)

        # Generate content using OpenAI
        result = generate_micro_sop(asset_type, prompt)

        if result is None:
            return Response({"error": "Failed to generate SOP. Try again."}, status=500)

        # Save generated asset
        asset = GeneratedAsset.objects.create(
            user=request.user,
            asset_type=asset_type,
            content=result,
            prompt_used=prompt
        )

        # Record credit usage
        UsageRecord.objects.create(
            user=request.user,
            credits_used=CREDITS_PER_SOP
        )

        return Response({
            "id": asset.id,
            "content": asset.content,
            "created_at": asset.created_at
        })


class UserAssetsView(ListAPIView):
    serializer_class = GeneratedAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GeneratedAsset.objects.filter(user=self.request.user).order_by("-created_at")
