# backend/generator/views.py
from django.shortcuts import render
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ratelimit.decorators import ratelimit

from generator.openai_client import generate_micro_sop
from generator.models import GeneratedAsset
from generator.serializers import GeneratedAssetSerializer

from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user
from billing.models import UsageRecord

CREDITS_PER_SOP = 1
ALLOWED_NICHES = {"general", "freelance", "consulting", "events", "coaching", "design"}


def _result_to_plain_text(result):
    try:
        if not isinstance(result, dict):
            return str(result)
        lines = []
        title = result.get("title")
        if title:
            lines += [title, ""]
        if result.get("body"):
            lines.append(result["body"])
        if result.get("sms"):
            lines += ["", "SMS:", result["sms"]]
        if result.get("checklist"):
            lines += ["", "Checklist:"]
            for i, item in enumerate(result["checklist"], 1):
                lines.append(f"{i}. {item}")
        if result.get("payment_note"):
            lines += ["", result["payment_note"]]
        if result.get("signature"):
            lines += ["", result["signature"]]
        return "\n".join(lines).strip() or str(result)
    except Exception:
        return str(result)


@method_decorator(
    [
        login_required,
        csrf_protect,
        ratelimit(key="user", rate="5/m", method="POST", block=True),
    ],
    name="dispatch",
)
class GenerateSOPView(View):
    """
    Handles both:
      - GET  → returns the modal form (generate_body.html)
      - POST → processes form and returns result partial (generate_result.html)
    """

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        ctx = {"form_data": {}, "niches": sorted(ALLOWED_NICHES)}
        return render(request, "frontend/modals/generate_body.html", ctx)

    def post(self, request):
        prompt = (request.POST.get("prompt") or "").strip()
        niche = (request.POST.get("niche") or "general").lower()
        language = (request.POST.get("language") or "en").lower()
        tone = (request.POST.get("tone") or "professional").lower()

        payment_method = (request.POST.get("payment_method") or "none").lower()
        payment_value = (request.POST.get("payment_value") or "").strip()
        add_to_calendar = bool(request.POST.get("add_to_calendar"))

        # --- Validation ---
        if not prompt:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": _("Prompt is required.")},
                status=400,
            )
        if niche not in ALLOWED_NICHES:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": _("Invalid niche.")},
                status=400,
            )
        if payment_method in {"mbway", "iban", "stripe"} and not payment_value:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": _("Please provide the payment value for the selected method.")},
                status=400,
            )

        # --- Credit check ---
        used = get_credits_used_this_month(request.user)
        limit = get_monthly_limit_for_user(request.user)
        if used + CREDITS_PER_SOP > limit:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": _("Credit limit reached for this month.")},
                status=403,
            )

        constraints = {
            "niche": niche,
            "tone": tone,
            "payment": {"method": payment_method, "value": payment_value},
            "calendar_hint": "Only extract date/time if explicitly and unambiguously stated.",
            "enable_calendar": add_to_calendar,
        }

        # --- Call generator + save ---
        try:
            with transaction.atomic():
                result_json = generate_micro_sop(
                    asset_type="auto",
                    prompt=prompt,
                    language=language,
                    tone=tone,
                    audience=request.POST.get("audience"),
                    constraints=constraints,
                    brand_voice=request.POST.get("brand_voice"),
                    include_signature=bool(request.POST.get("include_signature")),
                )

                GeneratedAsset.objects.create(
                    user=request.user,
                    asset_type="auto",
                    content=result_json,
                    prompt_used=prompt,
                )

                UsageRecord.objects.create(
                    user=request.user, credits_used=CREDITS_PER_SOP
                )

        except ValueError as e:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": f"Generation failed: {str(e)}"},
                status=502,
            )
        except TimeoutError:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": _("Upstream model timeout. Please try again.")},
                status=504,
            )
        except Exception:
            return render(
                request,
                "frontend/partials/generate_result.html",
                {"error": _("Unexpected error while generating.")},
                status=500,
            )

        plain_text = _result_to_plain_text(result_json)
        calendar_suggestion = (
            result_json.get("calendar") if add_to_calendar and isinstance(result_json, dict) else None
        )

        return render(
            request,
            "frontend/partials/generate_result.html",
            {"plain_text": plain_text, "calendar_suggestion": calendar_suggestion},
            status=201,
        )


class UserAssetsView(ListAPIView):
    serializer_class = GeneratedAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GeneratedAsset.objects.filter(user=self.request.user).order_by("-created_at")
