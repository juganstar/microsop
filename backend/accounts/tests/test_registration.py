import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

@pytest.mark.django_db
def test_registration_creates_user(client):
    url = reverse("custom-register")  # adjust to your actual route name
    data = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    resp = client.post(url, data)
    assert resp.status_code == 201
    assert get_user_model().objects.filter(email="test@example.com").exists()

@pytest.mark.django_db
def test_registration_duplicate_email(client):
    user_model = get_user_model()
    user_model.objects.create_user(email="test@example.com", password="pass")
    url = reverse("custom-register")
    data = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    resp = client.post(url, data)
    assert resp.status_code == 400
    assert b"already in use" in resp.content
