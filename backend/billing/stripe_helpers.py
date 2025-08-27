# backend/billing/stripe_helpers.py
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, price_id: str, plan_hint: str):
    """Create a Stripe Checkout Session for a subscription."""
    success_url = request.build_absolute_uri(reverse("billing:subscribe_success"))
    cancel_url  = request.build_absolute_uri(reverse("billing:subscribe_cancel"))

    # Attach user id + plan hint so webhook can update our DB
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        customer_email=getattr(request.user, "email", None),
        metadata={"user_id": request.user.id, "plan_hint": plan_hint},
    )
    return session

def create_billing_portal_session(request, customer_id: str):
    return_url = request.build_absolute_uri(reverse("home"))
    return stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
