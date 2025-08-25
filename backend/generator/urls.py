from django.urls import path
from .views import GenerateSOPView, UserAssetsView

urlpatterns = [
    # Clear, API-ish names to avoid clashing with frontend
    path("generate/form/",   GenerateSOPView.as_view(), name="api-generate-form"),
    path("generate/submit/", GenerateSOPView.as_view(), name="api-generate-sop"),

    path("my-assets/", UserAssetsView.as_view(), name="user_assets"),
]
