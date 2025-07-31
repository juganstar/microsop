from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dj_rest_auth.registration.views import RegisterView
from .serializers import CustomRegisterSerializer

def home(request):
    return render(request, "home.html")


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