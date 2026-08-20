from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from vehicles.models import Vehicle


class Maintenance(models.Model):

    # ==================================================
    # MAINTENANCE TYPE
    # ==================================================

    class MaintenanceType(models.TextChoices):
        REGULAR_SERVICE = "REGULAR_SERVICE", "Redovni servis"
        MAJOR_SERVICE = "MAJOR_SERVICE", "Veliki servis"
        OIL_CHANGE = "OIL_CHANGE", "Zamjena ulja"
        REPAIR = "REPAIR", "Popravak"
        TIRES = "TIRES", "Gume"
        DIAGNOSTICS = "DIAGNOSTICS", "Dijagnostika"
        OTHER = "OTHER", "Ostalo"


    # ==================================================
    # STATUS
    # ==================================================

    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planirano"
        IN_PROGRESS = "IN_PROGRESS", "U tijeku"
        COMPLETED = "COMPLETED", "Završeno"
        CANCELED = "CANCELED", "Otkazano"


    # ==================================================
    # VEHICLE / MACHINE
    # ==================================================

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="maintenances",
    )


    # ==================================================
    # BASIC INFORMATION
    # ==================================================

    title = models.CharField(
        max_length=150,
    )

    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    scheduled_date = models.DateField(
        blank=True,
        null=True,
    )

    completed_date = models.DateField(
        blank=True,
        null=True,
    )

    service_provider = models.CharField(
        max_length=150,
        blank=True,
    )


    # ==================================================
    # VEHICLE STATE AT MAINTENANCE
    # ==================================================

    mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    working_hours = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.0")),
        ],
    )


    # ==================================================
    # COST AND DESCRIPTION
    # ==================================================

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    description = models.TextField(
        blank=True,
    )


    # ==================================================
    # NEXT SERVICE
    # ==================================================

    next_service_date = models.DateField(
        blank=True,
        null=True,
    )

    next_service_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    next_service_working_hours = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.0")),
        ],
    )


    # ==================================================
    # TIMESTAMPS
    # ==================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )


    # ==================================================
    # META
    # ==================================================

    class Meta:
        ordering = [
            "-created_at",
        ]


    # ==================================================
    # STRING REPRESENTATION
    # ==================================================

    def __str__(self):
        return f"{self.vehicle.name} - {self.title}"