from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
@require_POST
def calendar_add(request):
    # In the future: create a real event (Google/ICS/etc.)
    title = (request.POST.get("title") or "").strip()
    date = (request.POST.get("date") or "").strip()
    start_time = (request.POST.get("start_time") or "").strip()
    end_time = (request.POST.get("end_time") or "").strip()
    # Minimal validation
    if not title or not date or not start_time:
        return JsonResponse({"ok": False, "msg": "Missing title/date/start time."}, status=400)
    return JsonResponse({"ok": True, "msg": "Event captured (stub)."}, status=201)
