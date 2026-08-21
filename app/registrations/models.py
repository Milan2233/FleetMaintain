from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from vehicles.models import Vehicle


class RegistrationInspection(models.Model):

    # ==============================================
    # RECORD TYPE
    # ==============================================

    class RecordType(models.TextChoices):
        REGISTRATION = "REGISTRATION", "Registracija"
        TECHNICAL_INSPECTION = (
            "TECHNICAL_INSPECTION",
            "Tehnički pregled",
        )


    # ==============================================
    # VEHICLE
    # ==============================================

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="registration_inspections",
    )


    # ==============================================
    # BASIC INFORMATION
    # ==============================================

    record_type = models.CharField(
        max_length=30,
        choices=RecordType.choices,
    )

    date = models.DateField()

    valid_until = models.DateField(
        blank=True,
        null=True,
    )

    provider = models.CharField(
        max_length=150,
        blank=True,
    )


    # ==============================================
    # VEHICLE STATE
    # ==============================================

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
            MinValueValidator(
                Decimal("0.0")
            )
        ],
    )


    # ==============================================
    # COST
    # ==============================================

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ],
    )


    # ==============================================
    # NOTE
    # ==============================================

    note = models.TextField(
        blank=True,
    )


    # ==============================================
    # SYSTEM
    # ==============================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:
        ordering = [
            "-date",
            "-created_at",
        ]


    def __str__(self):
        return (
            f"{self.vehicle.name} - "
            f"{self.get_record_type_display()}"
        )