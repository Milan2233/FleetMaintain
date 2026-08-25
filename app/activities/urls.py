from django.urls import path

from . import views


app_name = "activities"


urlpatterns = [

    # ==============================================
    # LIST
    # ==============================================

    path(
        "",
        views.activity_list_view,
        name="list",
    ),


    # ==============================================
    # MARK ONE AS READ
    # ==============================================

    path(
        "<int:pk>/procitano/",
        views.activity_mark_read_view,
        name="mark_read",
    ),


    # ==============================================
    # MARK ALL AS READ
    # ==============================================

    path(
        "procitaj-sve/",
        views.activity_mark_all_read_view,
        name="mark_all_read",
    ),

]