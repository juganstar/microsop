# backend/generator/views.py
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from generator.models import GeneratedAsset
from generator.serializers import GeneratedAssetSerializer
from django.conf import settings
import logging

from generator.forms import GenerateForm
from generator.presenters import result_to_plain_text
from generator.services.generation import generate_asset
from generator.services.persist import save_asset
from generator.services.credits import gate, record_success

from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

@method_decorator(login_required, name="dispatch")
@method_decorator(ratelimit(key="user", rate="5/m", method="POST", block=True), name="dispatch")
@method_decorator(ensure_csrf_cookie, name="get")
@method_decorator(csrf_protect, name="post")
class GenerateSOPView(View):
    def get(self, request):
        from generator.forms import ALLOWED_NICHES
        ctx = {"form_data": {}, "niches": sorted(ALLOWED_NICHES)}
        return render(request, "frontend/modals/generate_body.html", ctx)

    def post(self, request):
        form = GenerateForm(request.POST)
        if not form.is_valid():
            field, errors = next(iter(form.errors.items()))
            raw_msg = errors[0]

            friendly = {
                "prompt": _("Please describe what you need."),
                "payment_value": _("Please provide the payment value for the selected method."),
                "payment_method": _("Invalid payment method."),
                "niche": _("Invalid niche."),
            }.get(field, raw_msg)

            ctx = {"error": friendly}
            if settings.DEBUG:
                ctx["error_detail"] = f"{field}: {raw_msg}"  # shows e.g., "prompt: This field is required."
            return render(request, "frontend/partials/generate_result.html", ctx, status=200)

        ok, msg, used_before = gate(request.user)
        if not ok:
            return render(request, "frontend/partials/generate_result.html", {"error": _(msg)}, status=200)

        try:
            result = generate_asset(
                prompt=form.cleaned_data["prompt"],
                language=form.cleaned_data["language"],
                tone=form.cleaned_data["tone"],
                audience=form.cleaned_data.get("audience"),
                brand_voice=form.cleaned_data.get("brand_voice"),
                include_signature=bool(form.cleaned_data.get("include_signature")),
                constraints=form.constraints(),
            )
        except Exception as e:
            logger.exception("Generation failed")
            return render(request, "frontend/partials/generate_result.html",
                          {"error": _("Unexpected error while generating.")}, status=200)

        try:
            save_asset(user=request.user, prompt_used=form.cleaned_data["prompt"], content=result, asset_type="auto")
            record_success(request.user, used_before)
        except Exception:
            logger.exception("Persist/usage failed (non-fatal)")

        plain_text = result_to_plain_text(result)
        calendar_suggestion = result.get("calendar") if form.cleaned_data["add_to_calendar"] else None

        return render(request, "frontend/partials/generate_result.html",
                      {"plain_text": plain_text, "calendar_suggestion": calendar_suggestion},
                      status=201)

class UserAssetsView(ListAPIView):
    serializer_class = GeneratedAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GeneratedAsset.objects.filter(
            user=self.request.user
        ).order_by("-created_at")