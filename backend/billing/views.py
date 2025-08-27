# backend/billing/views.py
import json
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .stripe_helpers import create_checkout_session, create_billing_portal_session
from .models import Subscription

# --- Subscribe endpoints (create checkout session) ---

@login_required
@require_POST
def subscribe_basic(request):
    session = create_checkout_session(request, settings.STRIPE_PRICE_BASIC, plan_hint="basic")
    return JsonResponse({"url": session.url})

@login_required
@require_POST
def subscribe_premium(request):
    session = create_checkout_session(request, settings.STRIPE_PRICE_PREMIUM, plan_hint="premium")
    return JsonResponse({"url": session.url})

@login_required
@require_POST
def customer_portal(request):
    sub = Subscription.objects.get(user=request.user)
    if not sub.stripe_customer_id:
        return HttpResponseBadRequest("No Stripe customer on file.")
    portal = create_billing_portal_session(request, sub.stripe_customer_id)
    return JsonResponse({"url": portal.url})

# Optional landing pages
@login_required
def subscribe_success(request):
    return render(request, "billing/success.html")

@login_required
def subscribe_cancel(request):
    return render(request, "billing/cancel.html")

# --- Webhook: Stripe -> our DB ---

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE")
    secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception as e:
        return HttpResponseForbidden(str(e))

    etype = event["type"]
    data = event["data"]["object"]

    # 1) Checkout completed: set plan from metadata + save stripe ids
    if etype == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        plan_hint = data.get("metadata", {}).get("plan_hint")
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")

        if user_id and plan_hint:
            try:
                sub = Subscription.objects.select_for_update().get(user_id=user_id)
            except Subscription.DoesNotExist:
                return HttpResponse(status=200)

            sub.plan = plan_hint  # "basic" or "premium"
            sub.is_active = True
            sub.stripe_customer_id = customer_id or sub.stripe_customer_id
            sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id

            # If Stripe sends current period end (needs expand), we keep our monthly boundaries anyway.
            sub.save(update_fields=["plan", "is_active", "stripe_customer_id", "stripe_subscription_id"])
        return HttpResponse(status=200)

    # 2) Subscription updated (status changes, period ends, etc.)
    if etype == "customer.subscription.updated":
        sub_id = data.get("id")
        status = data.get("status")  # active, trialing, past_due, canceled, unpaid
        current_period_end = data.get("current_period_end")

        try:
            sub = Subscription.objects.get(stripe_subscription_id=sub_id)
        except Subscription.DoesNotExist:
            return HttpResponse(status=200)

        sub.is_active = status in ("active", "trialing")
        if current_period_end:
            sub.current_period_end = timezone.datetime.fromtimestamp(current_period_end, tz=timezone.utc)
        sub.save(update_fields=["is_active", "current_period_end"])
        return HttpResponse(status=200)

    # 3) Subscription canceled/deleted
    if etype in ("customer.subscription.deleted",):
        sub_id = data.get("id")
        try:
            sub = Subscription.objects.get(stripe_subscription_id=sub_id)
        except Subscription.DoesNotExist:
            return HttpResponse(status=200)

        # Downgrade back to trial (admin can still set free manually)
        sub.plan = "trial"
        sub.is_active = False
        sub.save(update_fields=["plan", "is_active"])
        return HttpResponse(status=200)

    return HttpResponse(status=200)
