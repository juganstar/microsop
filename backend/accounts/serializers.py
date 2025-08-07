from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.db import IntegrityError

from dj_rest_auth.serializers import LoginSerializer
from allauth.account.models import EmailAddress
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError(_("This email is already in use."))
        return email


    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return attrs

    def save(self):
        try:
            user = get_user_model().objects.create_user(
                email=self.validated_data['email'],
                password=self.validated_data['password1']
            )
            EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)  # <-- add this
        except IntegrityError:
            raise serializers.ValidationError(_("This email is already in use."))
        return user
    

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        user = self.user

        if not EmailAddress.objects.filter(user=user, verified=True).exists():
            raise serializers.ValidationError("Email not verified. Please confirm your email.")
        
        return validated_data
