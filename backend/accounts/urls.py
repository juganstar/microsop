from django.urls import path
from .views import home, user_me, ResendEmailVerificationView


urlpatterns = [
    path("", home, name="home"),
    path("me/", user_me, name="user-me"),
    path("resend-verification/", ResendEmailVerificationView.as_view(), name="resend-email-verification"),
]
