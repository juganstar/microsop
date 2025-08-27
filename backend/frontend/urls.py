# frontend/urls.py
from django.urls import path
from frontend.views.home import home
from frontend.views.dashboard import UsageTrackerView
from frontend.views.modals import trial_config_modal, login_modal, register_modal
from frontend.views.trial import activate_trial
from frontend.views.auth import register_submit, logout_submit
from frontend.views.calendar import calendar_add
from frontend.views.util import csrf_ping
from frontend.views.util import csrf_probe_form, csrf_probe_submit

# IMPORTANT: import the backend view for the form+submit
from backend.generator.views import GenerateSOPView

urlpatterns = [
    path("", home, name="home"),

    # Use the BACKEND view for the modal form (GET)
    path("api/generator/generate/form/",   GenerateSOPView.as_view(), name="api-generate-form"),
    # And for the submit (POST)
    path("api/generator/generate/submit/", GenerateSOPView.as_view(), name="api-generate-sop"),

    path("usage-tracker/", UsageTrackerView.as_view(), name="usage-tracker"),
    path("trial/config/", trial_config_modal, name="trial-config"),
    path("api/trial/activate/", activate_trial, name="activate-trial"),
    path("calendar/add/", calendar_add, name="calendar-add"),
    path("csrf/ping/", csrf_ping, name="csrf-ping"),
    path("csrf/probe/", csrf_probe_form, name="csrf-probe-form"),
    path("csrf/probe/submit/", csrf_probe_submit, name="csrf-probe-submit"),

    # MODALS
    path("modal/login/", login_modal, name="login-modal"),
    path("logout/", logout_submit, name="logout-submit"),
    path("modal/register/", register_modal, name="register-modal"),
    path("modal/register/submit/", register_submit, name="custom-register-htmx"),
]
