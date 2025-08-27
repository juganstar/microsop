from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_rest_auth.registration.views import RegisterView
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailAddress

from accounts.serializers import CustomRegisterSerializer
from django.views.decorators.csrf import ensure_csrf_cookie


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_me(request):
    user = request.user
    return Response({
        "id": user.id,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    })


class ResendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.emailaddress_set.filter(verified=True).exists():
            return Response({"detail": "Email is already verified."}, status=400)
        send_email_confirmation(request, user)
        return Response({"detail": "Verification email sent."})


def _render_login_body(request, errors=None, form_data=None, status=200):
    return render(
        request,
        "frontend/modals/login_body.html",
        {"errors": errors or {}, "form_data": form_data or {}},
        status=status,
    )


@require_POST
def login_htmx(request):
    email = (request.POST.get("email") or "").strip().lower()
    password = request.POST.get("password") or ""

    if not email or not password:
        return _render_login_body(
            request,
            errors={"non_field": "Preencha email e palavra-passe."},
            form_data={"email": email},
            status=422,
        )

    # Try both (depends on your AUTHENTICATION_BACKENDS / USERNAME_FIELD)
    user = authenticate(request, email=email, password=password) or \
           authenticate(request, username=email, password=password)

    if not user:
        return _render_login_body(
            request,
            errors={"non_field": "Email ou palavra-passe inválidos."},
            form_data={"email": email},
            status=422,
        )

    # Enforce verified email (same rule as your CustomLoginSerializer)
    if not EmailAddress.objects.filter(user=user, verified=True).exists():
        return _render_login_body(
            request,
            errors={"non_field": "Email não verificado. Confirme o seu email."},
            form_data={"email": email},
            status=422,
        )

    login(request, user)
    return JsonResponse({"key": "session", "detail": "login_ok"})


@require_POST
def logout_htmx(request):
    logout(request)
    return HttpResponse(status=204)
