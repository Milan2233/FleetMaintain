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

    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle,
        )

        if form.is_valid():

            form.save()

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

    vehicle.delete()

    messages.success(
        request,
        f'Vozilo / stroj "{vehicle_name}" uspješno je izbrisano.',
    )

    return redirect(
        "vehicles:list"
    )