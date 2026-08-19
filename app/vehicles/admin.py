from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "vehicle_type",
        "manufacturer",
        "model",
        "registration_number",
        "status",
        "user",
        "updated_at",
    )

    list_filter = (
        "vehicle_type",
        "fuel_type",
        "status",
    )

    search_fields = (
        "name",
        "manufacturer",
        "model",
        "registration_number",
        "vin_serial_number",
        "user__email",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )