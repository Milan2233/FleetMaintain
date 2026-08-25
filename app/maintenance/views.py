from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MaintenanceForm
from .models import Maintenance
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

from activities.models import Activity
from activities.services import log_activity


# ==================================================
# MAINTENANCE LIST
# ==================================================

@login_required
def maintenance_list_view(request):

    # ==============================================
    # USER MAINTENANCES
    # ==============================================

    base_maintenances = (
        Maintenance.objects
        .filter(vehicle__user=request.user)
        .select_related("vehicle")
    )


    # ==============================================
    # STATISTICS
    # ==============================================

    today = timezone.localdate()

    upcoming_limit = today + timedelta(days=30)


    total_maintenances = (
        base_maintenances.count()
    )


    upcoming_maintenances = (
        base_maintenances
        .filter(
            Q(
                status=Maintenance.Status.PLANNED,
                scheduled_date__gte=today,
                scheduled_date__lte=upcoming_limit,
            )
            |
            Q(
                next_service_date__gte=today,
                next_service_date__lte=upcoming_limit,
            )
        )
        .distinct()
        .count()
    )


    overdue_maintenances = (
        base_maintenances
        .filter(
            scheduled_date__lt=today,
        )
        .exclude(
            status__in=[
                Maintenance.Status.COMPLETED,
                Maintenance.Status.CANCELED,
            ]
        )
        .count()
    )


    total_costs = (
        base_maintenances
        .aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )


    # Queryset koji dalje koriste search/filteri
    maintenances = base_maintenances


    # ==============================================
    # SEARCH
    # ==============================================

    search_query = request.GET.get(
        "search",
        "",
    ).strip()

    if search_query:
        maintenances = maintenances.filter(
            Q(title__icontains=search_query)
            | Q(vehicle__name__icontains=search_query)
            | Q(vehicle__manufacturer__icontains=search_query)
            | Q(vehicle__model__icontains=search_query)
            | Q(vehicle__registration_number__icontains=search_query)
            | Q(service_provider__icontains=search_query)
            | Q(description__icontains=search_query)
        )


    # ==============================================
    # STATUS FILTER
    # ==============================================

    status_filter = request.GET.get(
        "status",
        "",
    )

    if status_filter:
        maintenances = maintenances.filter(
            status=status_filter
        )


    # ==============================================
    # MAINTENANCE TYPE FILTER
    # ==============================================

    type_filter = request.GET.get(
        "type",
        "",
    )

    if type_filter:
        maintenances = maintenances.filter(
            maintenance_type=type_filter
        )


    # ==============================================
    # VEHICLE FILTER
    # ==============================================

    vehicle_filter = request.GET.get(
        "vehicle",
        "",
    )

    if vehicle_filter:
        maintenances = maintenances.filter(
            vehicle_id=vehicle_filter
        )


    # ==============================================
    # PAGINATION
    # ==============================================

    paginator = Paginator(
        maintenances,
        8,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    # ==============================================
    # USER VEHICLES
    # ==============================================

    vehicles = request.user.vehicles.all()


    # ==============================================
    # CONTEXT
    # ==============================================

    context = {
        "maintenances": page_obj,
        "page_obj": page_obj,

        "search_query": search_query,
        "status_filter": status_filter,
        "type_filter": type_filter,
        "vehicle_filter": vehicle_filter,

        "status_choices": Maintenance.Status.choices,
        "type_choices": Maintenance.MaintenanceType.choices,

        "vehicles": vehicles,

        "total_maintenances": total_maintenances,
        "upcoming_maintenances": upcoming_maintenances,
        "overdue_maintenances": overdue_maintenances,
        "total_costs": total_costs,
    }

    return render(
        request,
        "maintenance/maintenance_list.html",
        context,
    )


# ==================================================
# CREATE MAINTENANCE
# ==================================================

@login_required
def maintenance_create_view(request):

    if request.method == "POST":

        form = MaintenanceForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            maintenance = form.save()

            log_activity(
                user=request.user,
                vehicle=maintenance.vehicle,
                activity_type=Activity.ActivityType.MAINTENANCE_CREATED,
                title="Dodano održavanje",
                description=(
                    f"{maintenance.vehicle.name} — "
                    f"{maintenance.title}"
                ),
            )            

            messages.success(
                request,
                "Održavanje je uspješno dodano.",
            )

            return redirect(
                "maintenance:list"
            )

    else:

        initial = {}


        # ==============================================
        # PRESELECT VEHICLE
        # ==============================================

        vehicle_id = request.GET.get(
            "vehicle"
        )

        if (
            vehicle_id
            and request.user.vehicles.filter(
                pk=vehicle_id
            ).exists()
        ):
            initial["vehicle"] = vehicle_id


        form = MaintenanceForm(
            user=request.user,
            initial=initial,
        )


    context = {
        "form": form,
    }

    return render(
        request,
        "maintenance/maintenance_form.html",
        context,
    )

# ==================================================
# MAINTENANCE DETAIL
# ==================================================

@login_required
def maintenance_detail_view(request, pk):

    maintenance = get_object_or_404(
        Maintenance.objects.select_related("vehicle"),
        pk=pk,
        vehicle__user=request.user,
    )

    context = {
        "maintenance": maintenance,
    }

    return render(
        request,
        "maintenance/maintenance_detail.html",
        context,
    )


# ==================================================
# UPDATE MAINTENANCE
# ==================================================

@login_required
def maintenance_update_view(request, pk):

    maintenance = get_object_or_404(
        Maintenance,
        pk=pk,
        vehicle__user=request.user,
    )


    if request.method == "POST":

        form = MaintenanceForm(
            request.POST,
            instance=maintenance,
            user=request.user,
        )


        if form.is_valid():

            has_changed = form.has_changed()

            maintenance = form.save()


            if has_changed:

                log_activity(
                    user=request.user,
                    vehicle=maintenance.vehicle,
                    activity_type=Activity.ActivityType.MAINTENANCE_UPDATED,
                    title="Ažurirano održavanje",
                    description=(
                        f"{maintenance.vehicle.name} — "
                        f"{maintenance.title}"
                    ),
                )


            messages.success(
                request,
                "Održavanje je uspješno ažurirano.",
            )

            return redirect(
                "maintenance:detail",
                pk=maintenance.pk,
            )


    else:

        form = MaintenanceForm(
            instance=maintenance,
            user=request.user,
        )


    context = {
        "form": form,
        "maintenance": maintenance,
        "is_edit": True,
    }


    return render(
        request,
        "maintenance/maintenance_form.html",
        context,
    )


# ==================================================
# DELETE MAINTENANCE
# ==================================================

@login_required
@require_POST
def maintenance_delete_view(request, pk):

    maintenance = get_object_or_404(
        Maintenance,
        pk=pk,
        vehicle__user=request.user,
    )

    maintenance_title = maintenance.title
    vehicle = maintenance.vehicle
    vehicle_name = vehicle.name


    log_activity(
        user=request.user,
        vehicle=vehicle,
        activity_type=Activity.ActivityType.MAINTENANCE_DELETED,
        title="Obrisano održavanje",
        description=(
            f"{vehicle_name} — "
            f"{maintenance_title}"
        ),
    )


    maintenance.delete()


    messages.success(
        request,
        f'Održavanje "{maintenance_title}" uspješno je izbrisano.',
    )

    return redirect(
        "maintenance:list"
    )