from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MaintenanceForm
from .models import Maintenance


# ==================================================
# MAINTENANCE LIST
# ==================================================

@login_required
def maintenance_list_view(request):

    maintenances = (
        Maintenance.objects
        .filter(vehicle__user=request.user)
        .select_related("vehicle")
    )


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

            form.save()

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

    maintenance.delete()

    messages.success(
        request,
        f'Održavanje "{maintenance_title}" uspješno je izbrisano.',
    )

    return redirect(
        "maintenance:list"
    )