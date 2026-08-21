from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.views.decorators.http import require_POST

from vehicles.models import Vehicle

from .forms import VehicleDocumentForm
from .models import VehicleDocument


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

            document = form.save()

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