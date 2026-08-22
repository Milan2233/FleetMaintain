from django.urls import path

from . import views


app_name = "costs"


urlpatterns = [

    path(
        "",
        views.cost_list_view,
        name="list",
    ),

]