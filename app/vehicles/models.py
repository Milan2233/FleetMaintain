from django.conf import settings
from django.db import models


class Vehicle(models.Model):

    # ==================================================
    # VEHICLE TYPE
    # ==================================================

    class VehicleType(models.TextChoices):
        CAR = "CAR", "Osobno vozilo"
        VAN = "VAN", "Kombi"
        TRUCK = "TRUCK", "Kamion"
        BUS = "BUS", "Autobus"
        TRACTOR = "TRACTOR", "Traktor"
        EXCAVATOR = "EXCAVATOR", "Bager"
        LOADER = "LOADER", "Utovarivač"
        FORKLIFT = "FORKLIFT", "Viličar"
        OTHER = "OTHER", "Ostalo"


    # ==================================================
    # FUEL TYPE
    # ==================================================

    class FuelType(models.TextChoices):
        PETROL = "PETROL", "Benzin"
        DIESEL = "DIESEL", "Dizel"
        HYBRID = "HYBRID", "Hibrid"
        PLUG_IN_HYBRID = "PHEV", "Plug-in hibrid"
        ELECTRIC = "ELECTRIC", "Električno"
        LPG = "LPG", "LPG"
        CNG = "CNG", "CNG"
        OTHER = "OTHER", "Ostalo"


    # ==================================================
    # STATUS
    # ==================================================

    class Status(models.TextChoices):
        OPERATIONAL = "OPERATIONAL", "Ispravno"
        IN_SERVICE = "IN_SERVICE", "U servisu"
        OUT_OF_ORDER = "OUT_OF_ORDER", "Neispravno"


    # ==================================================
    # OWNER
    # ==================================================

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )


    # ==================================================
    # BASIC INFORMATION
    # ==================================================

    name = models.CharField(
        max_length=150,
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
    )

    manufacturer = models.CharField(
        max_length=100,
    )

    model = models.CharField(
        max_length=100,
    )

    production_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
    )

    registration_number = models.CharField(
        max_length=30,
        blank=True,
    )

    vin_serial_number = models.CharField(
        max_length=100,
        blank=True,
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
        blank=True,
    )


    # ==================================================
    # OPERATIONAL INFORMATION
    # ==================================================

    current_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    working_hours = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPERATIONAL,
    )


    # ==================================================
    # ADDITIONAL INFORMATION
    # ==================================================

    note = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to="vehicles/",
        blank=True,
        null=True,
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
        ordering = ["-created_at"]


    # ==================================================
    # STRING REPRESENTATION
    # ==================================================

    def __str__(self):
        return f"{self.name} - {self.manufacturer} {self.model}"