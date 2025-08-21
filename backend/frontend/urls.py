from django.urls import path
from frontend.views.home import home
from frontend.views.dashboard import (
    GenerateFormView,
    GenerateSOPView,
    UserAssetsView,
    UsageTrackerView,
)

from frontend.views.modals import trial_config_modal, login_modal, register_modal
from frontend.views.trial import activate_trial
from frontend.views.auth import register_submit, logout_submit


urlpatterns = [
    path("", home, name="home"),
    path("generate/form/", GenerateFormView.as_view(), name="generate-form"),
    path("generate/", GenerateSOPView.as_view(), name="generate-sop"),
    path("my-assets/", UserAssetsView.as_view(), name="user-assets"),
    path("usage-tracker/", UsageTrackerView.as_view(), name="usage-tracker"),
    path("trial/config/", trial_config_modal, name="trial-config"),
    path("api/trial/activate/", activate_trial, name="activate-trial"),

    # MODALS
    path("modal/login/", login_modal, name="login-modal"),
    path("logout/", logout_submit, name="logout-submit"),
    path("modal/register/", register_modal, name="register-modal"),  # GET
    path("modal/register/submit/", register_submit, name="custom-register-htmx"),  # POST
]
