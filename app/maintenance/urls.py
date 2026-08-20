from django.urls import path

from .views import (
    maintenance_create_view,
    maintenance_delete_view,
    maintenance_detail_view,
    maintenance_list_view,
    maintenance_update_view,
)


app_name = "maintenance"


urlpatterns = [
    path(
        "",
        maintenance_list_view,
        name="list",
    ),

    path(
        "novo/",
        maintenance_create_view,
        name="create",
    ),
    path(
        "<int:pk>/",
        maintenance_detail_view,
        name="detail",
    ),

    path(
        "<int:pk>/uredi/",
        maintenance_update_view,
        name="update",
    ),

    path(
        "<int:pk>/izbrisi/",
        maintenance_delete_view,
        name="delete",
    ),    
]