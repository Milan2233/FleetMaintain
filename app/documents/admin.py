from django.contrib import admin

from .models import VehicleDocument


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):

    # ==============================================
    # LIST
    # ==============================================

    list_display = (
        "name",
        "vehicle",
        "document_type",
        "issue_date",
        "valid_until",
        "created_at",
    )

    list_filter = (
        "document_type",
        "issue_date",
        "valid_until",
    )

    search_fields = (
        "name",
        "vehicle__name",
        "vehicle__manufacturer",
        "vehicle__model",
        "vehicle__registration_number",
        "description",
    )

    ordering = (
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
                    "name",
                    "document_type",
                    "file",
                )
            },
        ),

        (
            "Datumi",
            {
                "fields": (
                    "issue_date",
                    "valid_until",
                )
            },
        ),

        (
            "Dodatne informacije",
            {
                "fields": (
                    "description",
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