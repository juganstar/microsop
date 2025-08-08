from django.core.management import call_command

def test_django_system_check_runs():
    # Fails if there are critical config errors
    call_command("check")
