from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponseNotAllowed

# Project imports
from accounts.serializers import CustomRegisterSerializer



@require_http_methods(["GET"])
def login_modal(request):
    # Initial render of the modal with the login form body partial
    return render(request, "frontend/modals/login.html", {"errors": {}})

@require_POST
def login_submit(request):
    # HTMX POST target
    email = (request.POST.get("email") or "").strip()
    password = request.POST.get("password") or ""

    # If your auth uses email-as-username, authenticate with username=email.
    user = authenticate(request, username=email, password=password)

    if user is None:
        # Re-render only the body with errors (what HTMX expects)
        ctx = {"errors": {"__all__": ["Credenciais inválidas."]}, "email": email}
        return render(request, "frontend/modals/login_body.html", ctx, status=400)

    login(request, user)

    # For HTMX, redirect the browser (closes modal + refreshes UI)
    resp = redirect("home")
    resp["HX-Redirect"] = reverse("home")
    return resp

def register_submit(request):
    if request.method == "POST":
        serializer = CustomRegisterSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()  # Correctly call the save method
            login(request, user)  # Log the user in
            return JsonResponse({"key": "logged_in"}, status=201)
        else:
            form_data = request.POST.copy()
            return render(request, "frontend/modals/register_body.html", {
                "errors": serializer.errors,
                "form_data": form_data,
            }, status=400)
    return HttpResponseNotAllowed(["POST"])

@require_POST
def logout_submit(request):
    """Log the user out and redirect home. Plays nice with HTMX too."""
    logout(request)

    # If the request came via HTMX, ask the browser to redirect.
    if request.headers.get("HX-Request"):
        resp = redirect("home")
        resp["HX-Redirect"] = reverse("home")
        return resp

    return redirect("home")