from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from dj_rest_auth.serializers import LoginSerializer
from allauth.account.models import EmailAddress

class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Kill username
    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
            "password2": self.validated_data.get("password2", ""),
        }
    

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        user = self.user

        if not EmailAddress.objects.filter(user=user, verified=True).exists():
            raise serializers.ValidationError("Email not verified. Please confirm your email.")
        
        return validated_data
