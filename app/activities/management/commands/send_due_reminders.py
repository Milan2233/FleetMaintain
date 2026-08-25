from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import NotificationSettings
from maintenance.models import Maintenance
from registrations.models import RegistrationInspection

from activities.models import Activity, ReminderLog


class Command(BaseCommand):

    help = (
        "Provjerava nadolazeća održavanja, registracije "
        "i tehničke preglede te kreira upozorenja."
    )


    def handle(self, *args, **options):

        today = timezone.localdate()

        notification_settings = (
            NotificationSettings.objects
            .select_related("user")
            .all()
        )


        for user_settings in notification_settings:

            user = user_settings.user

            reminder_days = (
                user_settings.get_reminder_days()
            )


            # Ako korisnik nije odabrao niti jedan interval,
            # nema što provjeravati.

            if not reminder_days:
                continue


            for days_before in reminder_days:

                due_date = (
                    today
                    + timedelta(
                        days=days_before
                    )
                )


                # ==========================================
                # PLANNED MAINTENANCE
                # ==========================================

                planned_maintenances = (
                    Maintenance.objects
                    .filter(
                        vehicle__user=user,
                        scheduled_date=due_date,
                    )
                    .exclude(
                        status__in=[
                            Maintenance.Status.COMPLETED,
                            Maintenance.Status.CANCELED,
                        ]
                    )
                    .select_related(
                        "vehicle",
                    )
                )


                for maintenance in planned_maintenances:

                    self.process_reminder(
                        user_settings=user_settings,
                        reminder_type=(
                            ReminderLog
                            .ReminderType
                            .MAINTENANCE
                        ),
                        object_id=maintenance.pk,
                        due_date=due_date,
                        days_before=days_before,
                        vehicle=maintenance.vehicle,
                        activity_type=(
                            Activity
                            .ActivityType
                            .MAINTENANCE_REMINDER
                        ),
                        title="Održavanje uskoro dospijeva",
                        description=(
                            f"{maintenance.vehicle.name} — "
                            f"{maintenance.title} — "
                            f"rok {due_date.strftime('%d.%m.%Y.')}"
                        ),
                    )


                # ==========================================
                # RECOMMENDED NEXT SERVICE
                # ==========================================

                recommended_maintenances = (
                    Maintenance.objects
                    .filter(
                        vehicle__user=user,
                        next_service_date=due_date,
                    )
                    .select_related(
                        "vehicle",
                    )
                )


                for maintenance in recommended_maintenances:

                    self.process_reminder(
                        user_settings=user_settings,
                        reminder_type=(
                            ReminderLog
                            .ReminderType
                            .MAINTENANCE
                        ),
                        object_id=maintenance.pk,
                        due_date=due_date,
                        days_before=days_before,
                        vehicle=maintenance.vehicle,
                        activity_type=(
                            Activity
                            .ActivityType
                            .MAINTENANCE_REMINDER
                        ),
                        title="Preporučeni servis se približava",
                        description=(
                            f"{maintenance.vehicle.name} — "
                            f"{maintenance.title} — "
                            f"rok {due_date.strftime('%d.%m.%Y.')}"
                        ),
                    )


                # ==========================================
                # REGISTRATION / TECHNICAL INSPECTION
                # ==========================================

                registration_records = (
                    RegistrationInspection.objects
                    .filter(
                        vehicle__user=user,
                        valid_until=due_date,
                    )
                    .select_related(
                        "vehicle",
                    )
                )


                for registration in registration_records:

                    if (
                        registration.record_type
                        ==
                        RegistrationInspection
                        .RecordType
                        .REGISTRATION
                    ):

                        reminder_type = (
                            ReminderLog
                            .ReminderType
                            .REGISTRATION
                        )

                        activity_type = (
                            Activity
                            .ActivityType
                            .REGISTRATION_REMINDER
                        )

                        title = (
                            "Registracija uskoro istječe"
                        )

                    else:

                        reminder_type = (
                            ReminderLog
                            .ReminderType
                            .TECHNICAL_INSPECTION
                        )

                        activity_type = (
                            Activity
                            .ActivityType
                            .TECHNICAL_INSPECTION_REMINDER
                        )

                        title = (
                            "Tehnički pregled uskoro istječe"
                        )


                    self.process_reminder(
                        user_settings=user_settings,
                        reminder_type=reminder_type,
                        object_id=registration.pk,
                        due_date=due_date,
                        days_before=days_before,
                        vehicle=registration.vehicle,
                        activity_type=activity_type,
                        title=title,
                        description=(
                            f"{registration.vehicle.name} — "
                            f"rok {due_date.strftime('%d.%m.%Y.')}"
                        ),
                    )


        self.stdout.write(
            self.style.SUCCESS(
                "Provjera podsjetnika završena."
            )
        )


    # ==================================================
    # PROCESS REMINDER
    # ==================================================

    def process_reminder(
        self,
        *,
        user_settings,
        reminder_type,
        object_id,
        due_date,
        days_before,
        vehicle,
        activity_type,
        title,
        description,
    ):

        user = user_settings.user


        # ==============================================
        # REMINDER LOG
        # ==============================================

        reminder_log, created = (
            ReminderLog.objects.get_or_create(
                user=user,
                reminder_type=reminder_type,
                object_id=object_id,
                due_date=due_date,
                days_before=days_before,
                defaults={
                    "vehicle": vehicle,
                },
            )
        )


        # ==============================================
        # CREATE IN-APP WARNING
        # ==============================================

        if not reminder_log.activity_created:

            Activity.objects.create(
                user=user,
                vehicle=vehicle,
                activity_type=activity_type,
                level=Activity.Level.WARNING,
                title=title,
                description=description,
                is_read=False,
            )

            reminder_log.activity_created = True

            reminder_log.save(
                update_fields=[
                    "activity_created",
                    "updated_at",
                ]
            )


        # ==============================================
        # EMAIL
        # ==============================================

        if (
            user_settings.email_enabled
            and not reminder_log.email_sent
        ):

            email_address = (
                user_settings
                .get_notification_email()
            )


            if email_address:

                subject = (
                    f"FleetMaintain – {title}"
                )

                message = (
                    f"{title}\n\n"
                    f"{description}\n\n"
                    f"Preostalo dana: {days_before}\n\n"
                    f"FleetMaintain"
                )


                try:

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=(
                            settings.DEFAULT_FROM_EMAIL
                        ),
                        recipient_list=[
                            email_address,
                        ],
                        fail_silently=False,
                    )

                except Exception as error:

                    self.stderr.write(
                        self.style.ERROR(
                            (
                                f"Email nije poslan korisniku "
                                f"{user.email}: {error}"
                            )
                        )
                    )

                else:

                    reminder_log.email_sent = True

                    reminder_log.save(
                        update_fields=[
                            "email_sent",
                            "updated_at",
                        ]
                    )