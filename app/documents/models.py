from django.db import models

from vehicles.models import Vehicle


class VehicleDocument(models.Model):

    # ==============================================
    # DOCUMENT TYPE
    # ==============================================

    class DocumentType(models.TextChoices):
        REGISTRATION = (
            "REGISTRATION",
            "Prometna dozvola",
        )

        INSURANCE = (
            "INSURANCE",
            "Polica osiguranja",
        )

        TECHNICAL = (
            "TECHNICAL",
            "Tehnička dokumentacija",
        )

        SERVICE = (
            "SERVICE",
            "Servisna dokumentacija",
        )

        PURCHASE = (
            "PURCHASE",
            "Dokumentacija o kupnji",
        )

        WARRANTY = (
            "WARRANTY",
            "Jamstvo",
        )

        OTHER = (
            "OTHER",
            "Ostalo",
        )


    # ==============================================
    # VEHICLE
    # ==============================================

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="documents",
    )


    # ==============================================
    # BASIC INFORMATION
    # ==============================================

    name = models.CharField(
        max_length=150,
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )

    file = models.FileField(
        upload_to="vehicle_documents/",
    )


    # ==============================================
    # DATES
    # ==============================================

    issue_date = models.DateField(
        blank=True,
        null=True,
    )

    valid_until = models.DateField(
        blank=True,
        null=True,
    )


    # ==============================================
    # NOTE
    # ==============================================

    description = models.TextField(
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
            "-created_at",
        ]


    def __str__(self):
        return (
            f"{self.vehicle.name} - "
            f"{self.name}"
        )