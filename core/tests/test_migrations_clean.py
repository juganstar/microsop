import io
import pytest
from django.core.management import call_command

@pytest.mark.django_db
def test_no_missing_migrations():
    out = io.StringIO()
    try:
        call_command("makemigrations", "--check", "--dry-run", stdout=out, stderr=out)
    except SystemExit as e:
        assert e.code == 0, out.getvalue()
