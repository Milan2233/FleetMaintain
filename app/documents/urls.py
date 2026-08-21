from django.urls import path

from . import views


app_name = "documents"


urlpatterns = [

    # CREATE
    path(
        "novo/",
        views.document_create_view,
        name="create",
    ),

    # UPDATE
    path(
        "<int:pk>/uredi/",
        views.document_update_view,
        name="update",
    ),

    # DELETE
    path(
        "<int:pk>/izbrisi/",
        views.document_delete_view,
        name="delete",
    ),

]