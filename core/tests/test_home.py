import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_home_page(client):
    url = reverse("home")
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"Micro-SOP" in resp.content  # adjust to match actual template text
