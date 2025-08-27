from django.db.models import Sum
from django.utils import timezone
from .models import UsageRecord, Subscription

PLAN_SPECS = {
    "free":    {"monthly": float("inf")},  # unlimited
    "trial":   {"monthly": 0},             # limited by trial_remaining
    "basic":   {"monthly": 100},
    "premium": {"monthly": 200},
}

def _month_bounds(dt=None):
    now = dt or timezone.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end

def get_credits_used_this_month(user) -> int:
    start, end = _month_bounds()
    return (
        UsageRecord.objects
        .filter(user=user, timestamp__gte=start, timestamp__lt=end)
        .aggregate(total=Sum("credits_used"))["total"]
        or 0
    )

def ensure_subscription(user) -> Subscription:
    sub = getattr(user, "subscription", None)
    if sub:
        return sub
    # EVERYONE starts on trial (admin can flip to 'free' anytime)
    return Subscription.objects.create(
        user=user, plan="trial", trial_remaining=5, included_credits=0, top_up_credits=0, is_active=True
    )

def get_plan_monthly_base(sub: Subscription) -> int:
    base = PLAN_SPECS.get(sub.plan, PLAN_SPECS["trial"]).get("monthly", 0)
    return 10**9 if base == float("inf") else int(base)

def credit_gate(user, amount: int = 1, used_this_month: int | None = None):
    """
    Returns (ok, msg). Stripe sets plan to basic/premium; admin can set 'free'.
    Trial is limited by trial_remaining only.
    """
    sub = ensure_subscription(user)

    if sub.plan == "free":
        return True, None

    if sub.plan == "trial":
        if sub.trial_remaining >= amount:
            return True, None
        return False, "Trial limit reached."

    base = get_plan_monthly_base(sub)
    if used_this_month is None:
        used_this_month = get_credits_used_this_month(user)
    allowed_total = base + sub.top_up_credits
    if used_this_month + amount > allowed_total:
        return False, "Insufficient credits."
    return True, None

def consume_post_success(user, amount: int = 1, used_before: int = 0):
    sub = ensure_subscription(user)

    if sub.plan == "free":
        return

    if sub.plan == "trial":
        if sub.trial_remaining >= amount:
            sub.trial_remaining -= amount
            sub.save(update_fields=["trial_remaining"])
        return

    base = get_plan_monthly_base(sub)
    if used_before >= base and sub.top_up_credits >= amount:
        sub.top_up_credits -= amount
        sub.save(update_fields=["top_up_credits"])

def get_monthly_limit_for_user(user) -> int:
    sub = ensure_subscription(user)
    if sub.plan == "free":
        return 10**9
    if sub.plan == "trial":
        return sub.trial_remaining
    base = get_plan_monthly_base(sub)
    return base + sub.top_up_credits
