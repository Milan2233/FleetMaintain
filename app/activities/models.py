from django.conf import settings
from django.db import models

from vehicles.models import Vehicle


class Activity(models.Model):

    # ==============================================
    # ACTIVITY TYPES
    # ==============================================

    class ActivityType(models.TextChoices):

        VEHICLE_CREATED = (
            "VEHICLE_CREATED",
            "Dodano vozilo / stroj",
        )

        VEHICLE_UPDATED = (
            "VEHICLE_UPDATED",
            "Ažurirano vozilo / stroj",
        )

        VEHICLE_STATUS_CHANGED = (
            "VEHICLE_STATUS_CHANGED",
            "Promijenjen status vozila / stroja",
        )

        VEHICLE_DELETED = (
            "VEHICLE_DELETED",
            "Obrisano vozilo / stroj",
        )


        MAINTENANCE_CREATED = (
            "MAINTENANCE_CREATED",
            "Dodano održavanje",
        )

        MAINTENANCE_UPDATED = (
            "MAINTENANCE_UPDATED",
            "Ažurirano održavanje",
        )

        MAINTENANCE_DELETED = (
            "MAINTENANCE_DELETED",
            "Obrisano održavanje",
        )


        REGISTRATION_CREATED = (
            "REGISTRATION_CREATED",
            "Dodana registracija / tehnički pregled",
        )

        REGISTRATION_UPDATED = (
            "REGISTRATION_UPDATED",
            "Ažurirana registracija / tehnički pregled",
        )

        REGISTRATION_DELETED = (
            "REGISTRATION_DELETED",
            "Obrisana registracija / tehnički pregled",
        )


        DOCUMENT_CREATED = (
            "DOCUMENT_CREATED",
            "Dodan dokument",
        )

        DOCUMENT_UPDATED = (
            "DOCUMENT_UPDATED",
            "Ažuriran dokument",
        )

        DOCUMENT_DELETED = (
            "DOCUMENT_DELETED",
            "Obrisan dokument",
        )

        MAINTENANCE_REMINDER = (
            "MAINTENANCE_REMINDER",
            "Podsjetnik za održavanje",
        )

        REGISTRATION_REMINDER = (
            "REGISTRATION_REMINDER",
            "Podsjetnik za registraciju",
        )

        TECHNICAL_INSPECTION_REMINDER = (
            "TECHNICAL_INSPECTION_REMINDER",
            "Podsjetnik za tehnički pregled",
        )


    # ==============================================
    # ACTIVITY LEVEL
    # ==============================================

    class Level(models.TextChoices):

        INFO = (
            "INFO",
            "Informacija",
        )

        WARNING = (
            "WARNING",
            "Upozorenje",
        )


    # ==============================================
    # RELATIONS
    # ==============================================

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )


    # ==============================================
    # ACTIVITY DATA
    # ==============================================

    activity_type = models.CharField(
        max_length=40,
        choices=ActivityType.choices,
    )

    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.INFO,
    )

    title = models.CharField(
        max_length=150,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    # ==============================================
    # META
    # ==============================================

    class Meta:

        ordering = [
            "-created_at",
        ]

        verbose_name = "Aktivnost"
        verbose_name_plural = "Aktivnosti"


    def __str__(self):

        return self.title

# ==================================================
# REMINDER LOG
# ==================================================

class ReminderLog(models.Model):

    # ==============================================
    # REMINDER TYPES
    # ==============================================

    class ReminderType(models.TextChoices):

        MAINTENANCE = (
            "MAINTENANCE",
            "Održavanje",
        )

        REGISTRATION = (
            "REGISTRATION",
            "Registracija",
        )

        TECHNICAL_INSPECTION = (
            "TECHNICAL_INSPECTION",
            "Tehnički pregled",
        )


    # ==============================================
    # RELATIONS
    # ==============================================

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reminder_logs",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_logs",
    )


    # ==============================================
    # REMINDER DATA
    # ==============================================

    reminder_type = models.CharField(
        max_length=30,
        choices=ReminderType.choices,
    )

    object_id = models.PositiveIntegerField()

    due_date = models.DateField()

    days_before = models.PositiveSmallIntegerField()


    # ==============================================
    # DELIVERY STATUS
    # ==============================================

    activity_created = models.BooleanField(
        default=False,
    )

    email_sent = models.BooleanField(
        default=False,
    )


    # ==============================================
    # TIMESTAMPS
    # ==============================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )


    # ==============================================
    # META
    # ==============================================

    class Meta:

        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "reminder_type",
                    "object_id",
                    "due_date",
                    "days_before",
                ],
                name="unique_due_reminder",
            ),
        ]

        verbose_name = "Evidencija podsjetnika"
        verbose_name_plural = "Evidencije podsjetnika"


    def __str__(self):

        return (
            f"{self.get_reminder_type_display()} — "
            f"{self.due_date} — "
            f"{self.days_before} dana"
        )    