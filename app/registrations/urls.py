from django.urls import path

from . import views


app_name = "registrations"


urlpatterns = [

    # CREATE
    path(
        "novo/",
        views.registration_create_view,
        name="create",
    ),

    # UPDATE
    path(
        "<int:pk>/uredi/",
        views.registration_update_view,
        name="update",
    ),

    # DELETE
    path(
        "<int:pk>/izbrisi/",
        views.registration_delete_view,
        name="delete",
    ),

]