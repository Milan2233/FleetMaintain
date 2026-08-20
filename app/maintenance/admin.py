from django.contrib import admin

from .models import Maintenance


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "vehicle",
        "maintenance_type",
        "status",
        "scheduled_date",
        "completed_date",
        "cost",
        "updated_at",
    )

    list_filter = (
        "maintenance_type",
        "status",
        "scheduled_date",
        "completed_date",
    )

    search_fields = (
        "title",
        "vehicle__name",
        "vehicle__manufacturer",
        "vehicle__model",
        "vehicle__registration_number",
        "service_provider",
        "description",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Osnovni podaci",
            {
                "fields": (
                    "vehicle",
                    "title",
                    "maintenance_type",
                    "status",
                    "scheduled_date",
                    "completed_date",
                    "service_provider",
                ),
            },
        ),

        (
            "Stanje vozila / stroja",
            {
                "fields": (
                    "mileage",
                    "working_hours",
                ),
            },
        ),

        (
            "Trošak i opis",
            {
                "fields": (
                    "cost",
                    "description",
                ),
            },
        ),

        (
            "Sljedeći servis",
            {
                "fields": (
                    "next_service_date",
                    "next_service_mileage",
                    "next_service_working_hours",
                ),
            },
        ),

        (
            "Sustav",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )