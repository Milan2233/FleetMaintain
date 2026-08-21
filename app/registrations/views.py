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

from .forms import RegistrationInspectionForm
from .models import RegistrationInspection


# ==============================================
# HELPERS
# ==============================================

def vehicle_registration_tab_url(vehicle):
    return (
        reverse(
            "vehicles:detail",
            args=[vehicle.pk],
        )
        + "?tab=registration"
    )


# ==============================================
# CREATE
# ==============================================

@login_required
def registration_create_view(request):

    initial = {}

    vehicle_id = request.GET.get("vehicle")

    if vehicle_id:

        vehicle = get_object_or_404(
            Vehicle,
            pk=vehicle_id,
            user=request.user,
        )

        initial["vehicle"] = vehicle


    if request.method == "POST":

        form = RegistrationInspectionForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            registration = form.save()

            messages.success(
                request,
                (
                    "Podaci o registraciji ili "
                    "tehničkom pregledu uspješno su spremljeni."
                ),
            )

            return redirect(
                vehicle_registration_tab_url(
                    registration.vehicle
                )
            )

    else:

        form = RegistrationInspectionForm(
            user=request.user,
            initial=initial,
        )


    context = {
        "form": form,
        "is_edit": False,
    }

    return render(
        request,
        "registrations/registration_form.html",
        context,
    )


# ==============================================
# UPDATE
# ==============================================

@login_required
def registration_update_view(
    request,
    pk,
):

    registration = get_object_or_404(
        RegistrationInspection,
        pk=pk,
        vehicle__user=request.user,
    )


    if request.method == "POST":

        form = RegistrationInspectionForm(
            request.POST,
            instance=registration,
            user=request.user,
        )

        if form.is_valid():

            registration = form.save()

            messages.success(
                request,
                (
                    "Podaci o registraciji ili "
                    "tehničkom pregledu uspješno su ažurirani."
                ),
            )

            return redirect(
                vehicle_registration_tab_url(
                    registration.vehicle
                )
            )

    else:

        form = RegistrationInspectionForm(
            instance=registration,
            user=request.user,
        )


    context = {
        "form": form,
        "registration": registration,
        "is_edit": True,
    }

    return render(
        request,
        "registrations/registration_form.html",
        context,
    )


# ==============================================
# DELETE
# ==============================================

@login_required
@require_POST
def registration_delete_view(
    request,
    pk,
):

    registration = get_object_or_404(
        RegistrationInspection,
        pk=pk,
        vehicle__user=request.user,
    )

    vehicle = registration.vehicle

    registration.delete()

    messages.success(
        request,
        (
            "Zapis registracije ili tehničkog "
            "pregleda uspješno je izbrisan."
        ),
    )

    return redirect(
        vehicle_registration_tab_url(
            vehicle
        )
    )