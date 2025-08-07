from django.contrib.auth import login  # Import the login function
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render
from accounts.serializers import CustomRegisterSerializer


def register_submit(request):
    if request.method == "POST":
        serializer = CustomRegisterSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()  # Correctly call the save method
            login(request, user)  # Log the user in
            return JsonResponse({"key": "logged_in"}, status=201)
        else:
            form_data = request.POST.copy()
            return render(request, "frontend/modals/register_modal.html", {
                "errors": serializer.errors,
                "form_data": form_data,
            }, status=400)
    return HttpResponseNotAllowed(["POST"])