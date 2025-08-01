from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from billing.models import Subscription  # ✅ Explicit import

CREDITS_PER_SOP = 1

class CheckAndConsumeCreditView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription = getattr(request.user, "subscription", None)
        if not subscription:
            return Response({"error": "Subscription not found."}, status=403)

        # ⛽ Auto top-up if low
        if subscription.should_auto_top_up():
            subscription.perform_auto_top_up()

        # 💥 Check again after top-up
        if subscription.get_total_credits() < CREDITS_PER_SOP:
            return Response({"error": "Insufficient credits."}, status=403)

        # 🔻 Deduct 1 credit
        try:
            subscription.consume_credit(CREDITS_PER_SOP)
        except ValueError:
            return Response({"error": "Insufficient credits."}, status=403)

        return Response({"success": "Credit consumed."})
