from django.shortcuts import render
from accounts.models import Profile  # importa o teu modelo de Profile
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def home(request):
    show_trial_modal = False

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.trial_shown:
            show_trial_modal = True
            profile.trial_shown = True
            profile.save()

    return render(request, "frontend/home.html", {"show_trial_modal": show_trial_modal})
