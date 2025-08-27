# create this file if it doesn't exist
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

@ensure_csrf_cookie
def csrf_ping(request):
    return JsonResponse({"ok": True})


@ensure_csrf_cookie
def csrf_probe_form(request):
    return render(request, "frontend/csrf_probe.html")

# Receives the POST; if CSRF is OK, this returns 200 "OK"
@csrf_protect
def csrf_probe_submit(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    return HttpResponse("OK", status=200)

# Optional: custom failure view that tells you WHY CSRF failed
def csrf_failure_view(request, reason=""):
    # You can return an HTML page; plain text is fine for debugging
    return HttpResponse(f"CSRF failed: {reason}", status=403)