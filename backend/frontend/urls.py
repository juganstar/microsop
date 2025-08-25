from django.urls import path
from frontend.views.home import home
from frontend.views.dashboard import (
    GenerateFormView,
    GenerateSOPView,
    UsageTrackerView,
)

from frontend.views.modals import trial_config_modal, login_modal, register_modal
from frontend.views.trial import activate_trial
from frontend.views.auth import register_submit, logout_submit
from frontend.views.calendar import calendar_add


urlpatterns = [
    path("", home, name="home"),
    path("generate/form/", GenerateFormView.as_view(), name="generate-form"),
    path("generate/", GenerateSOPView.as_view(), name="generate-sop"),
    path("usage-tracker/", UsageTrackerView.as_view(), name="usage-tracker"),
    path("trial/config/", trial_config_modal, name="trial-config"),
    path("api/trial/activate/", activate_trial, name="activate-trial"),
    path("calendar/add/", calendar_add, name="calendar-add"),

    # MODALS
    path("modal/login/", login_modal, name="login-modal"),
    path("logout/", logout_submit, name="logout-submit"),
    path("modal/register/", register_modal, name="register-modal"),  # GET
    path("modal/register/submit/", register_submit, name="custom-register-htmx"),  # POST
]
