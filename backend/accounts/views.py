from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dj_rest_auth.registration.views import RegisterView
from allauth.account.utils import send_email_confirmation
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.serializers import CustomRegisterSerializer 


def home(request):
    return render(request, "frontend/home.html")


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