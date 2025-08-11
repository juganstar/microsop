# backend/generator/views.py
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from generator.openai_client import generate_micro_sop
from generator.models import GeneratedAsset
from generator.serializers import GeneratedAssetSerializer

from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user
from billing.models import UsageRecord

from ratelimit.decorators import ratelimit

CREDITS_PER_SOP = 1
ALLOWED_TYPES = {"email", "checklist", "sms"}

@method_decorator(ratelimit(key="user", rate="5/m", method="POST", block=True), name="dispatch")
class GenerateSOPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = (request.data.get("prompt") or "").strip()
        asset_type = (request.data.get("asset_type") or "email").lower()
        language = (request.data.get("language") or "en").lower()
        tone = (request.data.get("tone") or "professional").lower()

        if not prompt:
            return Response({"error": "Prompt is required."}, status=status.HTTP_400_BAD_REQUEST)

        if asset_type not in ALLOWED_TYPES:
            return Response({"error": f"asset_type must be one of {sorted(ALLOWED_TYPES)}."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Credit gate
        used = get_credits_used_this_month(request.user)
        limit = get_monthly_limit_for_user(request.user)
        if used + CREDITS_PER_SOP > limit:
            return Response({"error": "Credit limit reached for this month."}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                # Generate via OpenAI (strict JSON)
                result = generate_micro_sop(
                    asset_type=asset_type,
                    prompt=prompt,
                    language=language,
                    tone=tone,
                    audience=request.data.get("audience"),
                    constraints=request.data.get("constraints"),
                    brand_voice=request.data.get("brand_voice"),
                    include_signature=bool(request.data.get("include_signature")),
                )

                # Persist asset
                asset = GeneratedAsset.objects.create(
                    user=request.user,
                    asset_type=asset_type,
                    content=result,     # JSONField
                    prompt_used=prompt,
                )

                # Consume credits
                UsageRecord.objects.create(
                    user=request.user,
                    credits_used=CREDITS_PER_SOP,
                )

        except ValueError as e:
            # e.g., schema mismatch / invalid JSON from the model
            return Response({"error": f"Generation failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
        except TimeoutError:
            return Response({"error": "Upstream model timeout. Please try again."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            # Log this in real life
            return Response({"error": "Unexpected error while generating."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(GeneratedAssetSerializer(asset).data, status=status.HTTP_201_CREATED)


class UserAssetsView(ListAPIView):
    serializer_class = GeneratedAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GeneratedAsset.objects.filter(user=self.request.user).order_by("-created_at")
