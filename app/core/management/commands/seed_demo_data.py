from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import NotificationSettings
from activities.models import Activity, ReminderLog
from documents.models import VehicleDocument
from maintenance.models import Maintenance
from registrations.models import RegistrationInspection
from vehicles.models import Vehicle


DEMO_VIN_PREFIX = "FM-DEMO-"


def shift_month(value, months, day=None):
    """
    Pomakni datum za zadani broj mjeseci.
    Negativan broj ide u prošlost, pozitivan u budućnost.
    """
    month_index = value.year * 12 + value.month - 1 + months
    year, month = divmod(month_index, 12)
    month += 1

    target_day = value.day if day is None else day
    target_day = min(
        target_day,
        monthrange(year, month)[1],
    )

    return date(
        year,
        month,
        target_day,
    )


class Command(BaseCommand):

    help = (
        "Generira realistične demo podatke za jednog postojećeg "
        "FleetMaintain korisnika."
    )


    def add_arguments(self, parser):

        parser.add_argument(
            "--email",
            required=True,
            help="Email postojećeg korisnika kojem se dodaju demo podaci.",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help=(
                "Prije generiranja briše samo FleetMaintain demo podatke "
                "tog korisnika."
            ),
        )


    @transaction.atomic
    def handle(self, *args, **options):

        email = options["email"].strip()
        clear_first = options["clear"]

        User = get_user_model()

        user = (
            User.objects
            .filter(
                email__iexact=email,
            )
            .first()
        )

        if not user:
            raise CommandError(
                f'Korisnik s email adresom "{email}" ne postoji.'
            )


        # ==================================================
        # CLEAR PREVIOUS DEMO DATA
        # ==================================================

        demo_vehicles = Vehicle.objects.filter(
            user=user,
            vin_serial_number__startswith=DEMO_VIN_PREFIX,
        )

        if demo_vehicles.exists():

            if not clear_first:
                raise CommandError(
                    "Demo podaci već postoje za ovog korisnika. "
                    "Pokreni naredbu ponovno s --clear."
                )

            self.stdout.write(
                "Brišem postojeće demo podatke..."
            )

            demo_vehicle_ids = list(
                demo_vehicles.values_list(
                    "id",
                    flat=True,
                )
            )

            demo_documents = VehicleDocument.objects.filter(
                vehicle_id__in=demo_vehicle_ids,
            )

            # FileField datoteke se ne brišu automatski iz storagea.
            for document in demo_documents:
                if document.file:
                    document.file.delete(
                        save=False,
                    )

            Activity.objects.filter(
                user=user,
                vehicle_id__in=demo_vehicle_ids,
            ).delete()

            ReminderLog.objects.filter(
                user=user,
                vehicle_id__in=demo_vehicle_ids,
            ).delete()

            demo_vehicles.delete()


        # ==================================================
        # NOTIFICATION SETTINGS
        # ==================================================

        # Ne mijenjamo postojeće korisničke postavke.
        # Ako ih korisnik još nema, kreiraju se s default vrijednostima.
        NotificationSettings.objects.get_or_create(
            user=user,
        )


        # ==================================================
        # VEHICLES / MACHINES
        # ==================================================

        vehicle_specs = [
            {
                "name": "VW Transporter",
                "vehicle_type": Vehicle.VehicleType.VAN,
                "manufacturer": "Volkswagen",
                "model": "Transporter T6",
                "production_year": 2020,
                "registration_number": "RI 1847 VT",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0001",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 128450,
                "working_hours": None,
                "status": Vehicle.Status.OPERATIONAL,
                "note": "Dostavno vozilo za svakodnevne terenske zadatke.",
                "base_cost": Decimal("260.00"),
            },
            {
                "name": "Renault Master",
                "vehicle_type": Vehicle.VehicleType.VAN,
                "manufacturer": "Renault",
                "model": "Master",
                "production_year": 2019,
                "registration_number": "RI 5321 RM",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0002",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 174200,
                "working_hours": None,
                "status": Vehicle.Status.IN_SERVICE,
                "note": "Kombi većeg teretnog kapaciteta.",
                "base_cost": Decimal("340.00"),
            },
            {
                "name": "Škoda Octavia",
                "vehicle_type": Vehicle.VehicleType.CAR,
                "manufacturer": "Škoda",
                "model": "Octavia",
                "production_year": 2021,
                "registration_number": "RI 9064 SO",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0003",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 89500,
                "working_hours": None,
                "status": Vehicle.Status.OPERATIONAL,
                "note": "Službeno osobno vozilo.",
                "base_cost": Decimal("180.00"),
            },
            {
                "name": "VW Golf GTE",
                "vehicle_type": Vehicle.VehicleType.CAR,
                "manufacturer": "Volkswagen",
                "model": "Golf GTE",
                "production_year": 2017,
                "registration_number": "RI 4612 GT",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0004",
                "fuel_type": Vehicle.FuelType.PLUG_IN_HYBRID,
                "current_mileage": 93500,
                "working_hours": None,
                "status": Vehicle.Status.OPERATIONAL,
                "note": "Plug-in hibridno osobno vozilo.",
                "base_cost": Decimal("230.00"),
            },
            {
                "name": "Mercedes Actros",
                "vehicle_type": Vehicle.VehicleType.TRUCK,
                "manufacturer": "Mercedes-Benz",
                "model": "Actros",
                "production_year": 2018,
                "registration_number": "RI 7741 MA",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0005",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": 312000,
                "working_hours": None,
                "status": Vehicle.Status.OPERATIONAL,
                "note": "Teretno vozilo za prijevoz opreme i materijala.",
                "base_cost": Decimal("680.00"),
            },
            {
                "name": "CAT 320",
                "vehicle_type": Vehicle.VehicleType.EXCAVATOR,
                "manufacturer": "Caterpillar",
                "model": "320",
                "production_year": 2020,
                "registration_number": "",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0006",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": None,
                "working_hours": Decimal("6420.5"),
                "status": Vehicle.Status.OUT_OF_ORDER,
                "note": "Bager za zemljane i građevinske radove.",
                "base_cost": Decimal("920.00"),
            },
            {
                "name": "JCB 3CX",
                "vehicle_type": Vehicle.VehicleType.LOADER,
                "manufacturer": "JCB",
                "model": "3CX",
                "production_year": 2019,
                "registration_number": "",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0007",
                "fuel_type": Vehicle.FuelType.DIESEL,
                "current_mileage": None,
                "working_hours": Decimal("5180.0"),
                "status": Vehicle.Status.OPERATIONAL,
                "note": "Kombinirani utovarivač za rad na terenu.",
                "base_cost": Decimal("610.00"),
            },
            {
                "name": "Linde H30",
                "vehicle_type": Vehicle.VehicleType.FORKLIFT,
                "manufacturer": "Linde",
                "model": "H30",
                "production_year": 2022,
                "registration_number": "",
                "vin_serial_number": f"{DEMO_VIN_PREFIX}0008",
                "fuel_type": Vehicle.FuelType.LPG,
                "current_mileage": None,
                "working_hours": Decimal("2140.5"),
                "status": Vehicle.Status.IN_SERVICE,
                "note": "Viličar za skladišne i logističke zadatke.",
                "base_cost": Decimal("280.00"),
            },
        ]

        created_vehicles = []

        for spec in vehicle_specs:

            base_cost = spec.pop("base_cost")

            vehicle = Vehicle.objects.create(
                user=user,
                **spec,
            )

            vehicle._demo_base_cost = base_cost
            created_vehicles.append(
                vehicle
            )


        # ==================================================
        # COMPLETED MAINTENANCE HISTORY
        # ==================================================

        today = timezone.localdate()

        maintenance_patterns = [
            {
                "title": "Redovni servis",
                "type": Maintenance.MaintenanceType.REGULAR_SERVICE,
                "factor": Decimal("1.00"),
                "description": "Redovni periodični servis vozila / stroja.",
            },
            {
                "title": "Zamjena ulja i filtera",
                "type": Maintenance.MaintenanceType.OIL_CHANGE,
                "factor": Decimal("0.55"),
                "description": "Zamijenjeno ulje i pripadajući filteri.",
            },
            {
                "title": "Dijagnostika",
                "type": Maintenance.MaintenanceType.DIAGNOSTICS,
                "factor": Decimal("0.35"),
                "description": "Provedena dijagnostika i kontrola sustava.",
            },
            {
                "title": "Popravak",
                "type": Maintenance.MaintenanceType.REPAIR,
                "factor": Decimal("1.55"),
                "description": "Izvršen popravak utvrđenog kvara.",
            },
            {
                "title": "Preventivni servis",
                "type": Maintenance.MaintenanceType.REGULAR_SERVICE,
                "factor": Decimal("0.85"),
                "description": "Preventivni pregled i zamjena potrošnih dijelova.",
            },
        ]

        month_offsets_by_vehicle = [
            [11, 8, 5, 2, 0],
            [10, 7, 4, 1, 0],
            [9, 6, 3, 1, 0],
            [11, 7, 4, 2, 0],
            [10, 8, 5, 3, 0],
            [9, 7, 5, 2, 0],
            [11, 6, 4, 1, 0],
            [10, 6, 3, 1, 0],
        ]

        maintenance_records = []

        for vehicle_index, vehicle in enumerate(
            created_vehicles
        ):

            base_cost = vehicle._demo_base_cost
            offsets = month_offsets_by_vehicle[
                vehicle_index
            ]

            for record_index, months_ago in enumerate(
                offsets
            ):

                pattern = maintenance_patterns[
                    record_index
                    % len(maintenance_patterns)
                ]

                completed_date = shift_month(
                    today,
                    -months_ago,
                    day=8 + (
                        vehicle_index
                        + record_index * 3
                    ) % 18,
                )

                if completed_date > today:
                    completed_date = today - timedelta(
                        days=1
                    )

                scheduled_date = (
                    completed_date
                    - timedelta(days=2)
                )

                cost = (
                    base_cost
                    * pattern["factor"]
                    * (
                        Decimal("1.00")
                        + Decimal(vehicle_index)
                        * Decimal("0.035")
                    )
                ).quantize(
                    Decimal("0.01")
                )

                mileage = None
                working_hours = None

                if vehicle.current_mileage is not None:

                    mileage = max(
                        1000,
                        vehicle.current_mileage
                        - months_ago * 1450
                        - record_index * 220,
                    )

                if vehicle.working_hours is not None:

                    working_hours = max(
                        Decimal("0.0"),
                        vehicle.working_hours
                        - Decimal(
                            str(
                                months_ago * 52
                                + record_index * 11
                            )
                        ),
                    )

                next_service_date = None
                next_service_mileage = None
                next_service_working_hours = None

                # Najnovijem završenom servisu dodaj
                # preporuku sljedećeg servisa.
                if record_index == len(offsets) - 1:

                    recommendation_days = [
                        14,
                        45,
                        25,
                        60,
                        90,
                        18,
                        70,
                        50,
                    ][vehicle_index]

                    next_service_date = (
                        today
                        + timedelta(
                            days=recommendation_days
                        )
                    )

                    if mileage is not None:
                        next_service_mileage = (
                            mileage + 15000
                        )

                    if working_hours is not None:
                        next_service_working_hours = (
                            working_hours
                            + Decimal("500.0")
                        )

                maintenance = Maintenance.objects.create(
                    vehicle=vehicle,
                    title=pattern["title"],
                    maintenance_type=pattern["type"],
                    status=Maintenance.Status.COMPLETED,
                    scheduled_date=scheduled_date,
                    completed_date=completed_date,
                    service_provider=(
                        "Auto Servis Rijeka"
                        if vehicle.current_mileage is not None
                        else "Servis radnih strojeva"
                    ),
                    mileage=mileage,
                    working_hours=working_hours,
                    cost=cost,
                    description=pattern["description"],
                    next_service_date=next_service_date,
                    next_service_mileage=next_service_mileage,
                    next_service_working_hours=(
                        next_service_working_hours
                    ),
                )

                maintenance_records.append(
                    maintenance
                )


        # ==================================================
        # CURRENT / FUTURE MAINTENANCE
        # ==================================================

        planned_specs = [
            {
                "vehicle": created_vehicles[0],
                "title": "Redovni servis",
                "type": Maintenance.MaintenanceType.REGULAR_SERVICE,
                "status": Maintenance.Status.PLANNED,
                "date": today + timedelta(days=5),
            },
            {
                "vehicle": created_vehicles[2],
                "title": "Zamjena ulja i filtera",
                "type": Maintenance.MaintenanceType.OIL_CHANGE,
                "status": Maintenance.Status.PLANNED,
                "date": today + timedelta(days=18),
            },
            {
                "vehicle": created_vehicles[4],
                "title": "Dijagnostika",
                "type": Maintenance.MaintenanceType.DIAGNOSTICS,
                "status": Maintenance.Status.PLANNED,
                "date": today + timedelta(days=45),
            },
            {
                "vehicle": created_vehicles[5],
                "title": "Popravak hidrauličkog sustava",
                "type": Maintenance.MaintenanceType.REPAIR,
                "status": Maintenance.Status.PLANNED,
                "date": today - timedelta(days=8),
            },
            {
                "vehicle": created_vehicles[1],
                "title": "Servis kočionog sustava",
                "type": Maintenance.MaintenanceType.REPAIR,
                "status": Maintenance.Status.IN_PROGRESS,
                "date": today - timedelta(days=2),
            },
            {
                "vehicle": created_vehicles[7],
                "title": "Preventivni servis",
                "type": Maintenance.MaintenanceType.REGULAR_SERVICE,
                "status": Maintenance.Status.IN_PROGRESS,
                "date": today,
            },
        ]

        planned_maintenance = []

        for item in planned_specs:

            vehicle = item["vehicle"]

            mileage = (
                vehicle.current_mileage
                if vehicle.current_mileage is not None
                else None
            )

            working_hours = (
                vehicle.working_hours
                if vehicle.working_hours is not None
                else None
            )

            record = Maintenance.objects.create(
                vehicle=vehicle,
                title=item["title"],
                maintenance_type=item["type"],
                status=item["status"],
                scheduled_date=item["date"],
                completed_date=None,
                service_provider="",
                mileage=mileage,
                working_hours=working_hours,
                cost=None,
                description=(
                    "Demo zapis za praćenje aktualnog "
                    "ili budućeg održavanja."
                ),
            )

            planned_maintenance.append(
                record
            )


        # ==================================================
        # REGISTRATIONS / TECHNICAL INSPECTIONS
        # ==================================================

        road_vehicle_types = {
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.VAN,
            Vehicle.VehicleType.TRUCK,
            Vehicle.VehicleType.BUS,
        }

        road_vehicles = [
            vehicle
            for vehicle in created_vehicles
            if vehicle.vehicle_type in road_vehicle_types
        ]

        for index, vehicle in enumerate(
            road_vehicles
        ):

            registration_date = shift_month(
                today,
                -(10 - index),
                day=5 + index * 2,
            )

            technical_date = (
                registration_date
                - timedelta(days=2)
            )

            mileage = (
                max(
                    1000,
                    vehicle.current_mileage
                    - (10 - index) * 1450,
                )
                if vehicle.current_mileage is not None
                else None
            )

            RegistrationInspection.objects.create(
                vehicle=vehicle,
                record_type=(
                    RegistrationInspection
                    .RecordType
                    .TECHNICAL_INSPECTION
                ),
                date=technical_date,
                valid_until=(
                    technical_date
                    + timedelta(days=365)
                ),
                provider=(
                    "Stanica za tehnički pregled Rijeka"
                ),
                mileage=mileage,
                cost=Decimal("52.00") + Decimal(index * 4),
                note="Redovni tehnički pregled.",
            )

            RegistrationInspection.objects.create(
                vehicle=vehicle,
                record_type=(
                    RegistrationInspection
                    .RecordType
                    .REGISTRATION
                ),
                date=registration_date,
                valid_until=(
                    registration_date
                    + timedelta(days=365)
                ),
                provider="Registracijski ured Rijeka",
                mileage=mileage,
                cost=(
                    Decimal("165.00")
                    + Decimal(index * 18)
                ),
                note="Redovno produženje registracije.",
            )


        # ==================================================
        # DOCUMENTS
        # ==================================================

        for vehicle in created_vehicles:

            if vehicle.vehicle_type in road_vehicle_types:

                document_specs = [
                    (
                        "Prometna dozvola",
                        VehicleDocument.DocumentType.REGISTRATION,
                        today - timedelta(days=180),
                        today + timedelta(days=185),
                    ),
                    (
                        "Polica osiguranja",
                        VehicleDocument.DocumentType.INSURANCE,
                        today - timedelta(days=160),
                        today + timedelta(days=205),
                    ),
                ]

            else:

                document_specs = [
                    (
                        "Tehnička dokumentacija",
                        VehicleDocument.DocumentType.TECHNICAL,
                        today - timedelta(days=500),
                        None,
                    ),
                    (
                        "Servisna dokumentacija",
                        VehicleDocument.DocumentType.SERVICE,
                        today - timedelta(days=90),
                        None,
                    ),
                ]

            for doc_index, (
                document_name,
                document_type,
                issue_date,
                valid_until,
            ) in enumerate(document_specs, start=1):

                document = VehicleDocument(
                    vehicle=vehicle,
                    name=document_name,
                    document_type=document_type,
                    issue_date=issue_date,
                    valid_until=valid_until,
                    description=(
                        "Demo dokument generiran za "
                        "testiranje FleetMaintain aplikacije."
                    ),
                )

                safe_vehicle_name = (
                    vehicle.name
                    .lower()
                    .replace(" ", "-")
                    .replace("/", "-")
                )

                filename = (
                    f"{safe_vehicle_name}-"
                    f"{doc_index}.txt"
                )

                file_content = (
                    f"FleetMaintain demo dokument\n\n"
                    f"Vozilo / stroj: {vehicle.name}\n"
                    f"Dokument: {document_name}\n"
                    f"Datum izdavanja: {issue_date}\n"
                )

                document.file.save(
                    filename,
                    ContentFile(
                        file_content.encode("utf-8")
                    ),
                    save=False,
                )

                document.save()


        # ==================================================
        # RECENT ACTIVITIES
        # ==================================================

        activity_specs = [
            {
                "days_ago": 0,
                "vehicle": created_vehicles[1],
                "type": Activity.ActivityType.MAINTENANCE_UPDATED,
                "level": Activity.Level.INFO,
                "title": "Ažurirano održavanje",
                "description": (
                    "Renault Master — servis kočionog sustava je u tijeku."
                ),
                "is_read": False,
            },
            {
                "days_ago": 1,
                "vehicle": created_vehicles[5],
                "type": Activity.ActivityType.MAINTENANCE_REMINDER,
                "level": Activity.Level.WARNING,
                "title": "Održavanje je prekoračeno",
                "description": (
                    "CAT 320 — popravak hidrauličkog sustava kasni 8 dana."
                ),
                "is_read": False,
            },
            {
                "days_ago": 2,
                "vehicle": created_vehicles[0],
                "type": Activity.ActivityType.MAINTENANCE_REMINDER,
                "level": Activity.Level.WARNING,
                "title": "Održavanje uskoro dospijeva",
                "description": (
                    "VW Transporter — redovni servis dospijeva za 5 dana."
                ),
                "is_read": False,
            },
            {
                "days_ago": 3,
                "vehicle": created_vehicles[7],
                "type": Activity.ActivityType.VEHICLE_STATUS_CHANGED,
                "level": Activity.Level.INFO,
                "title": "Promijenjen status vozila / stroja",
                "description": (
                    "Linde H30: Ispravno → U servisu"
                ),
                "is_read": True,
            },
            {
                "days_ago": 4,
                "vehicle": created_vehicles[3],
                "type": Activity.ActivityType.MAINTENANCE_UPDATED,
                "level": Activity.Level.INFO,
                "title": "Ažurirano održavanje",
                "description": (
                    "VW Golf GTE — evidentiran završeni servis."
                ),
                "is_read": True,
            },
            {
                "days_ago": 6,
                "vehicle": created_vehicles[4],
                "type": Activity.ActivityType.DOCUMENT_CREATED,
                "level": Activity.Level.INFO,
                "title": "Dodan dokument",
                "description": (
                    "Mercedes Actros — dodana prometna dozvola."
                ),
                "is_read": True,
            },
            {
                "days_ago": 8,
                "vehicle": created_vehicles[2],
                "type": Activity.ActivityType.REGISTRATION_UPDATED,
                "level": Activity.Level.INFO,
                "title": "Ažurirana registracija / tehnički pregled",
                "description": (
                    "Škoda Octavia — ažurirani registracijski podaci."
                ),
                "is_read": True,
            },
            {
                "days_ago": 10,
                "vehicle": created_vehicles[6],
                "type": Activity.ActivityType.MAINTENANCE_CREATED,
                "level": Activity.Level.INFO,
                "title": "Dodano održavanje",
                "description": (
                    "JCB 3CX — dodan preventivni servis."
                ),
                "is_read": True,
            },
            {
                "days_ago": 13,
                "vehicle": created_vehicles[5],
                "type": Activity.ActivityType.VEHICLE_STATUS_CHANGED,
                "level": Activity.Level.INFO,
                "title": "Promijenjen status vozila / stroja",
                "description": (
                    "CAT 320: Ispravno → Neispravno"
                ),
                "is_read": True,
            },
            {
                "days_ago": 16,
                "vehicle": created_vehicles[0],
                "type": Activity.ActivityType.DOCUMENT_CREATED,
                "level": Activity.Level.INFO,
                "title": "Dodan dokument",
                "description": (
                    "VW Transporter — dodana polica osiguranja."
                ),
                "is_read": True,
            },
            {
                "days_ago": 20,
                "vehicle": created_vehicles[4],
                "type": Activity.ActivityType.MAINTENANCE_UPDATED,
                "level": Activity.Level.INFO,
                "title": "Ažurirano održavanje",
                "description": (
                    "Mercedes Actros — evidentiran trošak servisa."
                ),
                "is_read": True,
            },
            {
                "days_ago": 24,
                "vehicle": created_vehicles[3],
                "type": Activity.ActivityType.VEHICLE_UPDATED,
                "level": Activity.Level.INFO,
                "title": "Ažurirano vozilo / stroj",
                "description": (
                    "VW Golf GTE — ažurirana kilometraža."
                ),
                "is_read": True,
            },
        ]

        for item in activity_specs:

            activity = Activity.objects.create(
                user=user,
                vehicle=item["vehicle"],
                activity_type=item["type"],
                level=item["level"],
                title=item["title"],
                description=item["description"],
                is_read=item["is_read"],
            )

            Activity.objects.filter(
                pk=activity.pk,
            ).update(
                created_at=(
                    timezone.now()
                    - timedelta(
                        days=item["days_ago"]
                    )
                )
            )


        # ==================================================
        # SUMMARY
        # ==================================================

        maintenance_count = Maintenance.objects.filter(
            vehicle__in=created_vehicles,
        ).count()

        registration_count = (
            RegistrationInspection.objects
            .filter(
                vehicle__in=created_vehicles,
            )
            .count()
        )

        document_count = VehicleDocument.objects.filter(
            vehicle__in=created_vehicles,
        ).count()

        activity_count = Activity.objects.filter(
            user=user,
            vehicle__in=created_vehicles,
        ).count()


        self.stdout.write(
            self.style.SUCCESS(
                "\nDemo podaci uspješno generirani."
            )
        )

        self.stdout.write(
            f"Korisnik: {user.email}"
        )

        self.stdout.write(
            f"Vozila / strojevi: {len(created_vehicles)}"
        )

        self.stdout.write(
            f"Održavanja: {maintenance_count}"
        )

        self.stdout.write(
            f"Registracije / tehnički: {registration_count}"
        )

        self.stdout.write(
            f"Dokumenti: {document_count}"
        )

        self.stdout.write(
            f"Aktivnosti: {activity_count}"
        )

        self.stdout.write(
            "\nNapomena: ReminderLog se namjerno ne generira "
            "kako demo podaci ne bi blokirali stvarne reminder testove."
        )
