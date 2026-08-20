from django.urls import path

from .views import (
    vehicle_create_view,
    vehicle_delete_view,
    vehicle_detail_view,
    vehicle_list_view,
    vehicle_update_view,
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
    path(
        "<int:pk>/",
        vehicle_detail_view,
        name="detail",
    ),
    path(
        "<int:pk>/uredi/",
        vehicle_update_view,
        name="update",
    ),

    path(
        "<int:pk>/izbrisi/",
        vehicle_delete_view,
        name="delete",
    ),    
]