from django.urls import path
from generator.views import GenerateSOPView, UserAssetsView

urlpatterns = [
    path("generate/", GenerateSOPView.as_view(), name="generate-sop"),
    path("my-assets/", UserAssetsView.as_view(), name="user_assets"),
]
