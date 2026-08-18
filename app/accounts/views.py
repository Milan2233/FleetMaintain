from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import EmailAuthenticationForm, RegistrationForm


def register_view(request):
    """
    Registracija novog korisnika.
    """

    # Ako je korisnik već prijavljen, nema potrebe
    # ponovno prikazivati registraciju.
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Korisnički račun uspješno je kreiran. Možete se prijaviti.",
            )

            return redirect("accounts:login")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


class CustomLoginView(LoginView):
    """
    Prijava korisnika putem e-mail adrese i lozinke.
    """

    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm

    # Ako je korisnik već prijavljen i ode na login,
    # preusmjeri ga na dashboard.
    redirect_authenticated_user = True

    # Nakon uspješne prijave.
    next_page = reverse_lazy("core:dashboard")


class CustomLogoutView(LogoutView):
    """
    Odjava korisnika.
    """

    next_page = reverse_lazy("accounts:login")