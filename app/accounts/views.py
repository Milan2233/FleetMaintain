from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import EmailAuthenticationForm, RegistrationForm


def register_view(request):
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
        {"form": form},
    )


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True
    next_page = reverse_lazy("core:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)

        remember_me = self.request.POST.get("remember_me")

        if remember_me:
            # Koristi standardno Django trajanje sesije
            # (zadano 14 dana)
            self.request.session.set_expiry(
                settings.SESSION_COOKIE_AGE
            )
        else:
            # Sesija prestaje nakon zatvaranja preglednika
            self.request.session.set_expiry(0)

        return response


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")