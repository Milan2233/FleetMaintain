from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import VehicleForm
from .models import Vehicle


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

    context = {
        "vehicle": vehicle,
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