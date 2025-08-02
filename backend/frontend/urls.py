from django.urls import path
from .views import (
    home,
    views,
    GenerateFormView,
    GenerateSOPView,
    UserAssetsView,
    UsageTrackerView
)

urlpatterns = [
    path("", home, name="home"),
    path("generate/form/", GenerateFormView.as_view(), name="generate-form"),
    path("generate/", GenerateSOPView.as_view(), name="generate-sop"),
    path("my-assets/", UserAssetsView.as_view(), name="user-assets"),
    path("usage-tracker/", UsageTrackerView.as_view(), name="usage-tracker"),
    path("trial/config/", views.trial_config_modal, name="trial-config"),
]
