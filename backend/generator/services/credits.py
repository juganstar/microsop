# backend/generator/services/credits.py
from billing.models import UsageRecord
CREDITS_PER_SOP = 1

USE_NEW_CREDIT = False
try:
    from billing.utils import get_credits_used_this_month, credit_gate, consume_post_success
    USE_NEW_CREDIT = True
except Exception:
    from billing.utils import get_credits_used_this_month, get_monthly_limit_for_user

def gate(user) -> tuple[bool, str | None, int]:
    used = get_credits_used_this_month(user)
    if USE_NEW_CREDIT:
        ok, msg = credit_gate(user, amount=CREDITS_PER_SOP, used_this_month=used)
        return ok, msg if not ok else None, used
    limit = get_monthly_limit_for_user(user)
    if used + CREDITS_PER_SOP > limit:
        return False, "Credit limit reached for this month.", used
    return True, None, used

def record_success(user, used_before: int):
    UsageRecord.objects.create(user=user, credits_used=CREDITS_PER_SOP)
    if USE_NEW_CREDIT:
        consume_post_success(user, amount=CREDITS_PER_SOP, used_before=used_before)
