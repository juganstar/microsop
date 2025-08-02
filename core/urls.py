from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import CustomRegisterView  # ✅ Custom view that avoids username bug

urlpatterns = [
    path("set-language/", set_language, name="set_language"),
]

urlpatterns += i18n_patterns(
    path("", include("frontend.urls")),
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", CustomRegisterView.as_view(), name="custom-register"),
    path("auth/", include("allauth.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),  # <-- ADICIONA ISTO
    path("api/generator/", include("backend.generator.urls")),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

