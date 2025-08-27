from django.urls import path
from .views import login_htmx, logout_htmx
from .views import user_me, ResendEmailVerificationView


urlpatterns = [
    path("me/", user_me, name="user-me"),
    path("resend-verification/", ResendEmailVerificationView.as_view(), name="resend-email-verification"),
    # HTMX auth (sem colidir com dj-rest_auth)
    path("auth/htmx/login/", login_htmx, name="auth_login_htmx"),
    path("auth/htmx/logout/", logout_htmx, name="auth_logout_htmx"),
]
