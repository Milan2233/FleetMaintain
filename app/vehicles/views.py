from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import VehicleForm
from .models import Vehicle
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse
from maintenance.models import Maintenance
from registrations.models import RegistrationInspection

from activities.models import Activity
from activities.services import log_activity


# ==================================================
# VEHICLE LIST
# ==================================================

@login_required
def vehicle_list_view(request):

    vehicles = Vehicle.objects.filter(
        user=request.user
    )

    # ==============================================
    # SEARCH
    # ==============================================

    search_query = request.GET.get(
        "search",
        "",
    ).strip()

    if search_query:
        vehicles = vehicles.filter(
            Q(name__icontains=search_query)
            | Q(manufacturer__icontains=search_query)
            | Q(model__icontains=search_query)
            | Q(registration_number__icontains=search_query)
            | Q(vin_serial_number__icontains=search_query)
        )

    # ==============================================
    # STATUS FILTER
    # ==============================================

    status_filter = request.GET.get(
        "status",
        "",
    )

    if status_filter:
        vehicles = vehicles.filter(
            status=status_filter
        )

    # ==============================================
    # VEHICLE TYPE FILTER
    # ==============================================

    type_filter = request.GET.get(
        "type",
        "",
    )

    if type_filter:
        vehicles = vehicles.filter(
            vehicle_type=type_filter
        )

    # ==============================================
    # PAGINATION
    # ==============================================

    paginator = Paginator(
        vehicles,
        8,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    # ==============================================
    # CONTEXT
    # ==============================================

    context = {
        "vehicles": page_obj,
        "page_obj": page_obj,

        "search_query": search_query,
        "status_filter": status_filter,
        "type_filter": type_filter,

        "status_choices": Vehicle.Status.choices,
        "type_choices": Vehicle.VehicleType.choices,

        "total_filtered": paginator.count,
    }

    return render(
        request,
        "vehicles/vehicle_list.html",
        context,
    )


# ==================================================
# CREATE VEHICLE
# ==================================================

@login_required
def vehicle_create_view(request):

    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            vehicle = form.save(
                commit=False
            )

            vehicle.user = request.user

            vehicle.save()

            log_activity(
                user=request.user,
                vehicle=vehicle,
                activity_type=Activity.ActivityType.VEHICLE_CREATED,
                title="Dodano novo vozilo / stroj",
                description=vehicle.name,
            )            

            messages.success(
                request,
                "Vozilo / stroj uspješno je dodano.",
            )

            return redirect(
                "vehicles:list"
            )

    else:

        form = VehicleForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "vehicles/vehicle_form.html",
        context,
    )

# ==================================================
# VEHICLE DETAIL
# ==================================================

@login_required
def vehicle_detail_view(request, pk):

    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        user=request.user,
    )

    # ==============================================
    # MAINTENANCE STATISTICS
    # ==============================================

    vehicle_maintenances = (
        vehicle.maintenances
        .all()
    )


    # Total number of maintenances

    total_maintenances = (
        vehicle_maintenances
        .count()
    )


    # Last completed maintenance

    last_maintenance = (
        vehicle_maintenances
        .filter(
            status="COMPLETED",
            completed_date__isnull=False,
        )
        .order_by(
            "-completed_date",
            "-created_at",
        )
        .first()
    )


    # ==============================================
    # NEXT SERVICE
    # ==============================================

    today = timezone.localdate()


    # Najbliže planirano održavanje

    next_planned_maintenance = (
        vehicle_maintenances
        .filter(
            scheduled_date__gte=today,
        )
        .exclude(
            status__in=[
                "COMPLETED",
                "CANCELED",
            ]
        )
        .order_by(
            "scheduled_date",
            "created_at",
        )
        .first()
    )


    # Preporučeni sljedeći servis iz zadnjeg
    # završenog održavanja

    recommended_service_date = None
    recommended_service_mileage = None
    recommended_service_working_hours = None

    if last_maintenance:

        recommended_service_date = (
            last_maintenance.next_service_date
        )

        recommended_service_mileage = (
            last_maintenance.next_service_mileage
        )

        recommended_service_working_hours = (
            last_maintenance.next_service_working_hours
        )


    # Odabir najbližeg sljedećeg servisa

    next_service_date = None
    next_service_mileage = None
    next_service_working_hours = None
    next_service_title = None
    next_service_is_planned = False
    next_service_overdue = False


    if (
        next_planned_maintenance
        and next_planned_maintenance.scheduled_date
        and (
            not recommended_service_date
            or
            next_planned_maintenance.scheduled_date
            <= recommended_service_date
        )
    ):

        next_service_date = (
            next_planned_maintenance.scheduled_date
        )

        next_service_title = (
            next_planned_maintenance.title
        )

        next_service_is_planned = True

    else:

        next_service_date = (
            recommended_service_date
        )

        next_service_mileage = (
            recommended_service_mileage
        )

        next_service_working_hours = (
            recommended_service_working_hours
        )


    if (
        next_service_date
        and next_service_date < today
    ):
        next_service_overdue = True

    # Total maintenance costs

    total_maintenance_cost = (
        vehicle_maintenances
        .aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )    


    # ==============================================
    # ACTIVE TAB
    # ==============================================

    active_tab = request.GET.get(
        "tab",
        "overview",
    )

    allowed_tabs = {
        "overview",
        "maintenance",
        "registration",
        "documents",
        "costs",
    }

    if active_tab not in allowed_tabs:
        active_tab = "overview"


    # ==============================================
    # VEHICLE MAINTENANCES
    # ==============================================

    maintenances = None

    if active_tab == "maintenance":

        maintenances = (
            vehicle.maintenances
            .all()
            .order_by(
                "-scheduled_date",
                "-created_at",
            )
        )

    # ==============================================
    # REGISTRATION / TECHNICAL INSPECTION
    # ==============================================

    registration_inspections = None

    if active_tab == "registration":

        registration_inspections = (
            vehicle.registration_inspections
            .all()
            .order_by(
                "-date",
                "-created_at",
            )
        ) 

    # ==============================================
    # REGISTRATION / INSPECTION STATISTICS
    # ==============================================

    current_registration = None
    last_technical_inspection = None

    next_obligation_date = None
    next_obligation_type = None
    next_obligation_days = None
    next_obligation_overdue = False

    registration_valid_days = None
    registration_expired = False

    total_registration_cost = Decimal("0.00")


    if active_tab == "registration":

        today = timezone.localdate()


        # ==========================================
        # CURRENT REGISTRATION
        # ==========================================

        current_registration = (
            vehicle.registration_inspections
            .filter(
                record_type="REGISTRATION",
            )
            .order_by(
                "-date",
                "-created_at",
            )
            .first()
        )


        # ==========================================
        # LAST TECHNICAL INSPECTION
        # ==========================================

        last_technical_inspection = (
            vehicle.registration_inspections
            .filter(
                record_type="TECHNICAL_INSPECTION",
            )
            .order_by(
                "-date",
                "-created_at",
            )
            .first()
        )


        # ==========================================
        # REGISTRATION VALIDITY
        # ==========================================

        if (
            current_registration
            and current_registration.valid_until
        ):

            registration_valid_days = (
                current_registration.valid_until
                - today
            ).days

            if registration_valid_days < 0:
                registration_expired = True


        # ==========================================
        # NEXT OBLIGATION
        # ==========================================

        obligations = []


        if (
            current_registration
            and current_registration.valid_until
        ):
            obligations.append(
                (
                    current_registration.valid_until,
                    "Registracija",
                )
            )


        if (
            last_technical_inspection
            and last_technical_inspection.valid_until
        ):
            obligations.append(
                (
                    last_technical_inspection.valid_until,
                    "Tehnički pregled",
                )
            )


        if obligations:

            next_obligation_date, next_obligation_type = min(
                obligations,
                key=lambda item: item[0],
            )

            next_obligation_days = (
                next_obligation_date
                - today
            ).days

            if next_obligation_days < 0:
                next_obligation_overdue = True


        # ==========================================
        # TOTAL COST
        # ==========================================

        total_registration_cost = (
            vehicle.registration_inspections
            .aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0.00")
        )     

    # ==============================================
    # VEHICLE DOCUMENTS
    # ==============================================

    vehicle_documents = None

    if active_tab == "documents":

        vehicle_documents = (
            vehicle.documents
            .all()
            .order_by(
                "-created_at",
            )
        )  

    # ==============================================
    # VEHICLE COSTS
    # ==============================================

    vehicle_cost_items = None

    vehicle_total_cost = Decimal("0.00")
    vehicle_maintenance_cost = Decimal("0.00")
    vehicle_registration_cost = Decimal("0.00")

    vehicle_last_cost = None

    vehicle_most_expensive_cost = None

    vehicle_cost_chart_labels = []
    vehicle_cost_chart_values = []

    vehicle_cost_distribution = []


    if active_tab == "costs":

        vehicle_cost_items = []


        # ==========================================
        # MAINTENANCE COSTS
        # ==========================================

        maintenance_costs = (
            vehicle.maintenances
            .filter(
                cost__isnull=False,
            )
        )


        vehicle_maintenance_cost = (
            maintenance_costs
            .aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0.00")
        )


        for maintenance in maintenance_costs:

            cost_date = (
                maintenance.completed_date
                or maintenance.scheduled_date
                or maintenance.created_at.date()
            )

            vehicle_cost_items.append(
                {
                    "date": cost_date,

                    "category": "Održavanje",

                    "description": maintenance.title,

                    "secondary": (
                        maintenance.get_maintenance_type_display()
                    ),

                    "amount": maintenance.cost,

                    "source_url": reverse(
                        "maintenance:detail",
                        args=[maintenance.pk],
                    ),
                }
            )


        # ==========================================
        # REGISTRATION / INSPECTION COSTS
        # ==========================================

        registration_costs = (
            vehicle.registration_inspections
            .filter(
                cost__isnull=False,
            )
        )


        vehicle_registration_cost = (
            registration_costs
            .aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0.00")
        )


        for registration in registration_costs:

            vehicle_cost_items.append(
                {
                    "date": registration.date,

                    "category": (
                        registration.get_record_type_display()
                    ),

                    "description": (
                        registration.get_record_type_display()
                    ),

                    "secondary": (
                        registration.provider
                        or "Registracija i tehnički pregled"
                    ),

                    "amount": registration.cost,

                    "source_url": reverse(
                        "registrations:update",
                        args=[registration.pk],
                    ),
                }
            )


        # ==========================================
        # TOTAL COST
        # ==========================================

        vehicle_total_cost = (
            vehicle_maintenance_cost
            + vehicle_registration_cost
        )


        # ==========================================
        # ORDERING
        # ==========================================

        vehicle_cost_items.sort(
            key=lambda item: item["date"],
            reverse=True,
        )


        # ==========================================
        # LAST COST
        # ==========================================

        if vehicle_cost_items:
            vehicle_last_cost = vehicle_cost_items[0]   

        # ==========================================
        # MOST EXPENSIVE COST
        # ==========================================

        vehicle_most_expensive_cost = None

        if vehicle_cost_items:

            vehicle_most_expensive_cost = max(
                vehicle_cost_items,
                key=lambda item: item["amount"],
            )


        # ==========================================
        # LAST 12 MONTHS CHART
        # ==========================================

        month_names = [
            "Sij",
            "Velj",
            "Ožu",
            "Tra",
            "Svi",
            "Lip",
            "Srp",
            "Kol",
            "Ruj",
            "Lis",
            "Stu",
            "Pro",
        ]


        today = timezone.localdate()

        months = []

        year = today.year
        month = today.month


        for _ in range(12):

            months.append(
                (
                    year,
                    month,
                )
            )

            month -= 1

            if month == 0:
                month = 12
                year -= 1


        months.reverse()


        vehicle_cost_chart_labels = []
        vehicle_cost_chart_values = []


        for year, month in months:

            vehicle_cost_chart_labels.append(
                f"{month_names[month - 1]} {str(year)[2:]}"
            )

            month_total = sum(
                (
                    item["amount"]
                    for item in vehicle_cost_items
                    if (
                        item["date"].year == year
                        and item["date"].month == month
                    )
                ),
                Decimal("0.00"),
            )

            vehicle_cost_chart_values.append(
                float(month_total)
            )


        # ==========================================
        # COST DISTRIBUTION
        # ==========================================

        vehicle_cost_distribution = []


        # MAINTENANCE TYPES

        for value, label in Maintenance.MaintenanceType.choices:

            amount = (
                maintenance_costs
                .filter(
                    maintenance_type=value,
                )
                .aggregate(
                    total=Sum("cost")
                )["total"]
                or Decimal("0.00")
            )

            vehicle_cost_distribution.append(
                {
                    "label": label,
                    "amount": amount,
                }
            )


        # REGISTRATION

        registration_amount = (
            registration_costs
            .filter(
                record_type=(
                    RegistrationInspection
                    .RecordType
                    .REGISTRATION
                )
            )
            .aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0.00")
        )

        vehicle_cost_distribution.append(
            {
                "label": "Registracija",
                "amount": registration_amount,
            }
        )


        # TECHNICAL INSPECTION

        technical_amount = (
            registration_costs
            .filter(
                record_type=(
                    RegistrationInspection
                    .RecordType
                    .TECHNICAL_INSPECTION
                )
            )
            .aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0.00")
        )

        vehicle_cost_distribution.append(
            {
                "label": "Tehnički pregled",
                "amount": technical_amount,
            }
        )


        # ==========================================
        # SORT DISTRIBUTION
        # ==========================================

        vehicle_cost_distribution.sort(
            key=lambda item: item["amount"],
            reverse=True,
        )                                 

    # ==============================================
    # CONTEXT
    # ==============================================

    context = {
        "vehicle": vehicle,
        "active_tab": active_tab,
        "maintenances": maintenances,

        "total_maintenances": total_maintenances,
        "last_maintenance": last_maintenance,

        "next_service_date": next_service_date,
        "next_service_mileage": next_service_mileage,
        "next_service_working_hours": next_service_working_hours,
        "next_service_overdue": next_service_overdue,
        "next_service_title": next_service_title,
        "next_service_is_planned": next_service_is_planned,        

        "total_maintenance_cost": total_maintenance_cost,

        "registration_inspections": registration_inspections,
        "current_registration": current_registration,
        "last_technical_inspection": last_technical_inspection,

        "registration_valid_days": registration_valid_days,
        "registration_expired": registration_expired,

        "next_obligation_date": next_obligation_date,
        "next_obligation_type": next_obligation_type,
        "next_obligation_days": next_obligation_days,
        "next_obligation_overdue": next_obligation_overdue,

        "total_registration_cost": total_registration_cost,

        "vehicle_documents": vehicle_documents,

        "vehicle_cost_items": vehicle_cost_items,

        "vehicle_total_cost": vehicle_total_cost,
        "vehicle_maintenance_cost": vehicle_maintenance_cost,
        "vehicle_registration_cost": vehicle_registration_cost,

        "vehicle_last_cost": vehicle_last_cost,
        "vehicle_most_expensive_cost": vehicle_most_expensive_cost,

        "vehicle_cost_chart_labels": vehicle_cost_chart_labels,
        "vehicle_cost_chart_values": vehicle_cost_chart_values,

        "vehicle_cost_distribution": vehicle_cost_distribution,
    }

    return render(
        request,
        "vehicles/vehicle_detail.html",
        context,
    )

# ==================================================
# UPDATE VEHICLE
# ==================================================

@login_required
def vehicle_update_view(request, pk):

    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        user=request.user,
    )

    old_status = vehicle.status


    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle,
        )

        if form.is_valid():

            vehicle = form.save()


            if old_status != vehicle.status:

                log_activity(
                    user=request.user,
                    vehicle=vehicle,
                    activity_type=Activity.ActivityType.VEHICLE_STATUS_CHANGED,
                    title="Promijenjen status vozila / stroja",
                    description=(
                        f"{vehicle.name}: "
                        f"{dict(Vehicle.Status.choices).get(old_status)} → "
                        f"{vehicle.get_status_display()}"
                    ),
                )

            elif form.has_changed():

                log_activity(
                    user=request.user,
                    vehicle=vehicle,
                    activity_type=Activity.ActivityType.VEHICLE_UPDATED,
                    title="Ažurirano vozilo / stroj",
                    description=vehicle.name,
                )


            messages.success(
                request,
                "Podaci o vozilu / stroju uspješno su ažurirani.",
            )

            return redirect(
                "vehicles:detail",
                pk=vehicle.pk,
            )

    else:

        form = VehicleForm(
            instance=vehicle,
        )


    context = {
        "form": form,
        "vehicle": vehicle,
        "is_edit": True,
    }

    return render(
        request,
        "vehicles/vehicle_form.html",
        context,
    )


# ==================================================
# DELETE VEHICLE
# ==================================================

@login_required
@require_POST
def vehicle_delete_view(request, pk):

    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        user=request.user,
    )

    vehicle_name = vehicle.name


    log_activity(
        user=request.user,
        vehicle=vehicle,
        activity_type=Activity.ActivityType.VEHICLE_DELETED,
        title="Obrisano vozilo / stroj",
        description=vehicle_name,
    )


    vehicle.delete()


    messages.success(
        request,
        f'Vozilo / stroj "{vehicle_name}" uspješno je izbrisano.',
    )

    return redirect(
        "vehicles:list"
    )