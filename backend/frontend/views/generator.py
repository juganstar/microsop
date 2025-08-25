from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.db import transaction

from generator.openai_client import generate_micro_sop
from generator.models import GeneratedAsset
from generator.serializers import GeneratedAssetSerializer

from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user
from billing.models import UsageRecord

CREDITS_PER_SOP = 1
ALLOWED_TYPES = {"email", "checklist", "sms"}
ALLOWED_NICHES = [
    ("general", "Geral"),
    ("freelance", "Freelancer/Serviços"),
    ("consulting", "Consultoria"),
    ("events", "Eventos"),
    ("coaching", "Coaching"),
    ("design", "Design"),
]

@require_GET
@login_required
def generator_modal(request):
    # Initial render of the modal shell + form (no result yet)
    ctx = {
        "form_data": {},
        "niches": ALLOWED_NICHES,
    }
    return render(request, "frontend/modals/generate_body.html", ctx)


def _result_to_plain_text(result):
    """
    Turns the model's JSON into a nice copyable plain text block.
    Expected keys (example): title, body, checklist(list), sms, payment_note, signature.
    We keep it resilient: if unknown shape, str(result).
    """
    try:
        if not isinstance(result, dict):
            return str(result)

        lines = []
        title = result.get("title")
        if title:
            lines.append(title)
            lines.append("")

        if "body" in result and result["body"]:
            lines.append(result["body"])

        if "sms" in result and result["sms"]:
            lines.append("")
            lines.append("SMS:")
            lines.append(result["sms"])

        if "checklist" in result and result["checklist"]:
            lines.append("")
            lines.append("Checklist:")
            for i, item in enumerate(result["checklist"], 1):
                lines.append(f"{i}. {item}")

        if "payment_note" in result and result["payment_note"]:
            lines.append("")
            lines.append(result["payment_note"])

        if "signature" in result and result["signature"]:
            lines.append("")
            lines.append(result["signature"])

        return "\n".join(lines).strip() or str(result)
    except Exception:
        return str(result)
