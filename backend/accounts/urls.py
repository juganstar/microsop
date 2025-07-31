from django.urls import path
from .views import home, user_me

urlpatterns = [
    path("", home, name="home"),
    path("me/", user_me, name="user-me"),
]
