from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse

from generator.models import GeneratedAsset
from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user
from generator.openai_client import generate_micro_sop

@method_decorator(login_required, name='dispatch')
class GenerateFormView(View):
    def get(self, request):
        return render(request, "frontend/modals/generate_body.html", {"form_data": {}, "errors": {}})


@method_decorator(login_required, name='dispatch')
class UsageTrackerView(View):
    def get(self, request):
        used = get_credits_used_this_month(request.user)
        limit = get_monthly_limit_for_user(request.user)
        return render(request, "frontend/partials/usage_stats.html", {"used": used, "limit": limit})
