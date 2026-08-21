from django.contrib import admin

from .models import RegistrationInspection


@admin.register(RegistrationInspection)
class RegistrationInspectionAdmin(admin.ModelAdmin):

    # ==============================================
    # LIST
    # ==============================================

    list_display = (
        "vehicle",
        "record_type",
        "date",
        "valid_until",
        "provider",
        "cost",
        "created_at",
    )

    list_filter = (
        "record_type",
        "date",
        "valid_until",
    )

    search_fields = (
        "vehicle__name",
        "vehicle__manufacturer",
        "vehicle__model",
        "vehicle__registration_number",
        "provider",
        "note",
    )

    ordering = (
        "-date",
        "-created_at",
    )


    # ==============================================
    # FORM
    # ==============================================

    fieldsets = (

        (
            "Osnovni podaci",
            {
                "fields": (
                    "vehicle",
                    "record_type",
                    "date",
                    "valid_until",
                    "provider",
                )
            },
        ),

        (
            "Stanje vozila / stroja",
            {
                "fields": (
                    "mileage",
                    "working_hours",
                )
            },
        ),

        (
            "Trošak i napomena",
            {
                "fields": (
                    "cost",
                    "note",
                )
            },
        ),

        (
            "Sustav",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )