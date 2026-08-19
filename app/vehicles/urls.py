from django.urls import path

from .views import (
    vehicle_create_view,
    vehicle_list_view,
)


app_name = "vehicles"


urlpatterns = [
    path(
        "",
        vehicle_list_view,
        name="list",
    ),
    path(
        "novo/",
        vehicle_create_view,
        name="create",
    ),
]