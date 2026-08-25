from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from vehicles.models import Vehicle

from .forms import VehicleDocumentForm
from .models import VehicleDocument

from activities.models import Activity
from activities.services import log_activity


# ==============================================
# HELPERS
# ==============================================

def vehicle_documents_tab_url(vehicle):

    return (
        reverse(
            "vehicles:detail",
            args=[vehicle.pk],
        )
        + "?tab=documents"
    )


# ==============================================
# CREATE
# ==============================================

@login_required
def document_create_view(request):

    initial = {}

    vehicle_id = request.GET.get("vehicle")


    # ==========================================
    # PRESELECT VEHICLE
    # ==========================================

    if vehicle_id:

        vehicle = get_object_or_404(
            Vehicle,
            pk=vehicle_id,
            user=request.user,
        )

        initial["vehicle"] = vehicle


    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        form = VehicleDocumentForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():

            document = form.save()

            log_activity(
                user=request.user,
                vehicle=document.vehicle,
                activity_type=Activity.ActivityType.DOCUMENT_CREATED,
                title="Dodan dokument",
                description=(
                    f"{document.vehicle.name} — "
                    f"{document.name}"
                ),
            )            

            messages.success(
                request,
                "Dokument je uspješno spremljen.",
            )

            return redirect(
                vehicle_documents_tab_url(
                    document.vehicle
                )
            )


    # ==========================================
    # GET
    # ==========================================

    else:

        form = VehicleDocumentForm(
            user=request.user,
            initial=initial,
        )


    context = {
        "form": form,
        "is_edit": False,
    }

    return render(
        request,
        "documents/document_form.html",
        context,
    )


# ==============================================
# UPDATE
# ==============================================

@login_required
def document_update_view(
    request,
    pk,
):

    document = get_object_or_404(
        VehicleDocument,
        pk=pk,
        vehicle__user=request.user,
    )


    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        form = VehicleDocumentForm(
            request.POST,
            request.FILES,
            instance=document,
            user=request.user,
        )

        if form.is_valid():

            has_changed = form.has_changed()

            document = form.save()


            if has_changed:

                log_activity(
                    user=request.user,
                    vehicle=document.vehicle,
                    activity_type=Activity.ActivityType.DOCUMENT_UPDATED,
                    title="Ažuriran dokument",
                    description=(
                        f"{document.vehicle.name} — "
                        f"{document.name}"
                    ),
                )

            messages.success(
                request,
                "Dokument je uspješno ažuriran.",
            )

            return redirect(
                vehicle_documents_tab_url(
                    document.vehicle
                )
            )


    # ==========================================
    # GET
    # ==========================================

    else:

        form = VehicleDocumentForm(
            instance=document,
            user=request.user,
        )


    context = {
        "form": form,
        "document": document,
        "is_edit": True,
    }

    return render(
        request,
        "documents/document_form.html",
        context,
    )


# ==============================================
# DELETE
# ==============================================

@login_required
@require_POST
def document_delete_view(
    request,
    pk,
):

    document = get_object_or_404(
        VehicleDocument,
        pk=pk,
        vehicle__user=request.user,
    )

    vehicle = document.vehicle
    vehicle_name = vehicle.name
    document_name = document.name


    log_activity(
        user=request.user,
        vehicle=vehicle,
        activity_type=Activity.ActivityType.DOCUMENT_DELETED,
        title="Obrisan dokument",
        description=(
            f"{vehicle_name} — "
            f"{document_name}"
        ),
    )


    document.delete()


    messages.success(
        request,
        "Dokument je uspješno izbrisan.",
    )

    return redirect(
        vehicle_documents_tab_url(
            vehicle
        )
    )