# frontend/views/trial.py

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@csrf_exempt
@login_required
def activate_trial(request):
    if request.method == "POST":
        asset_type = request.POST.get("asset_type")
        goal = request.POST.get("goal")

        profile = request.user.profile
        profile.preferred_asset = asset_type
        profile.trial_goal = goal
        profile.save()

        subscription = getattr(request.user, "subscription", None)
        if subscription and not subscription.trial_active:
            subscription.trial_active = True
            subscription.top_up_credits = 5
            subscription.save()

        return JsonResponse({
            "success": True,
            "message": "✅ Trial ativado com sucesso!",
        })

    return JsonResponse({"error": "Método não permitido"}, status=405)
