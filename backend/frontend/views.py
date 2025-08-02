from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse

from generator.models import GeneratedAsset
from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user
from generator.openai_client import generate_micro_sop


def home(request):
    show_trial_modal = False
    if request.user.is_authenticated and not request.user.profile.trial_shown:
        show_trial_modal = True
        request.user.profile.trial_shown = True
        request.user.profile.save()
    
    return render(request, "frontend/home.html", {"show_trial_modal": show_trial_modal})



@method_decorator(login_required, name='dispatch')
class GenerateFormView(View):
    def get(self, request):
        return render(request, "frontend/partials/generate_form.html")


@method_decorator(login_required, name='dispatch')
class GenerateSOPView(View):
    def post(self, request):
        prompt = request.POST.get("prompt")
        asset_type = request.POST.get("asset_type")

        if not prompt or not asset_type:
            return JsonResponse({"error": "Faltam dados."}, status=400)

        result = generate_micro_sop(asset_type, prompt)

        GeneratedAsset.objects.create(
            user=request.user,
            asset_type=asset_type,
            prompt_used=prompt,
            content=result
        )

        return render(request, "frontend/partials/generate_result.html", {"result": result})


@method_decorator(login_required, name='dispatch')
class UserAssetsView(View):
    def get(self, request):
        assets = GeneratedAsset.objects.filter(user=request.user).order_by("-created_at")[:20]
        return render(request, "frontend/partials/assets_list.html", {"assets": assets})


@method_decorator(login_required, name='dispatch')
class UsageTrackerView(View):
    def get(self, request):
        used = get_credits_used_this_month(request.user)
        limit = get_monthly_limit_for_user(request.user)
        return render(request, "frontend/partials/usage_stats.html", {"used": used, "limit": limit})


@login_required
def trial_config_modal(request):
    return render(request, "frontend/modals/trial_config_modal.html")