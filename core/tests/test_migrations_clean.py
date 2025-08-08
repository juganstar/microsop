# backend/core/tests/test_migrations_clean.py
import io
from django.core.management import call_command

def test_no_missing_migrations():
    # makemigrations --check exits non-zero when there are changes
    out = io.StringIO()
    try:
        call_command("makemigrations", "--check", "--dry-run", stdout=out, stderr=out)
    except SystemExit as e:
        assert e.code == 0, out.getvalue()
