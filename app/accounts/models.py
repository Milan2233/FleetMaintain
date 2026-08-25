from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

# ==================================================
# NOTIFICATION SETTINGS
# ==================================================

class NotificationSettings(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )

    # ==============================================
    # EMAIL
    # ==============================================

    email_enabled = models.BooleanField(
        default=False,
    )

    notification_email = models.EmailField(
        blank=True,
    )


    # ==============================================
    # REMINDER INTERVALS
    # ==============================================

    remind_30_days = models.BooleanField(
        default=False,
    )

    remind_7_days = models.BooleanField(
        default=False,
    )

    remind_1_day = models.BooleanField(
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
    # HELPERS
    # ==============================================

    def get_reminder_days(self):

        days = []

        if self.remind_30_days:
            days.append(30)

        if self.remind_7_days:
            days.append(7)

        if self.remind_1_day:
            days.append(1)

        return days


    def get_notification_email(self):

        return (
            self.notification_email
            or self.user.email
        )


    def __str__(self):

        return f"Postavke obavijesti — {self.user.email}"    