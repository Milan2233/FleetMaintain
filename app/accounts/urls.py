from django.urls import path

from .views import CustomLoginView, CustomLogoutView, register_view


app_name = "accounts"


urlpatterns = [
    path("prijava/", CustomLoginView.as_view(), name="login"),
    path("registracija/", register_view, name="register"),
    path("odjava/", CustomLogoutView.as_view(), name="logout"),
]