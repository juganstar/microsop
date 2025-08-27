from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("subscribe/basic/", views.subscribe_basic, name="subscribe_basic"),
    path("subscribe/premium/", views.subscribe_premium, name="subscribe_premium"),
    path("portal/", views.customer_portal, name="customer_portal"),
    path("success/", views.subscribe_success, name="subscribe_success"),
    path("cancel/", views.subscribe_cancel, name="subscribe_cancel"),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
]
