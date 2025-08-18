# frontend/views/modals.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def trial_config_modal(request):
    if request.method == "POST":
        preferred = request.POST.get("preferred_asset")
        request.user.profile.preferred_asset = preferred
        request.user.profile.save()

        return JsonResponse({
            "success": True,
            "message": "Trial ativado com sucesso!",
        })

    return render(request, "frontend/modals/trial_config_modal.html")


def login_modal(request):
    return render(request, "frontend/modals/login_body.html", {
        "form_data": request.POST or {},
        "errors": {},
    })

def register_modal(request):
    return render(request, "frontend/modals/register_body.html", {
        "errors": {},
        "form_data": {}
    })
