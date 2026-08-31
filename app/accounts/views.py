from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from .forms import EmailAuthenticationForm, RegistrationForm, NotificationSettingsForm, ProfileSettingsForm, SettingsPasswordChangeForm
from .models import NotificationSettings


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
                extra_tags="login-message",
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

# ==================================================
# SETTINGS
# ==================================================

@login_required
def settings_view(request):

    # ==============================================
    # ACTIVE TAB
    # ==============================================

    active_tab = request.GET.get(
        "tab",
        "profile",
    )

    allowed_tabs = {
        "profile",
        "notifications",
        "about",
    }

    if active_tab not in allowed_tabs:
        active_tab = "profile"


    # ==============================================
    # NOTIFICATION SETTINGS
    # ==============================================

    notification_settings, _ = (
        NotificationSettings.objects.get_or_create(
            user=request.user,
        )
    )


    # ==============================================
    # DEFAULT FORMS
    # ==============================================

    profile_form = ProfileSettingsForm(
        instance=request.user,
    )

    password_form = SettingsPasswordChangeForm(
        user=request.user,
    )

    notification_form = NotificationSettingsForm(
        instance=notification_settings,
    )


    # ==============================================
    # POST
    # ==============================================

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "",
        )


        # ==========================================
        # PROFILE DATA
        # ==========================================

        if action == "profile_data":

            active_tab = "profile"

            profile_form = ProfileSettingsForm(
                request.POST,
                instance=request.user,
            )

            if profile_form.is_valid():

                profile_form.save()

                messages.success(
                    request,
                    "Osobni podaci uspješno su spremljeni.",
                )

                return redirect(
                    f"{reverse('accounts:settings')}?tab=profile"
                )


        # ==========================================
        # PASSWORD CHANGE
        # ==========================================

        elif action == "password_change":

            active_tab = "profile"

            password_form = SettingsPasswordChangeForm(
                user=request.user,
                data=request.POST,
            )

            if password_form.is_valid():

                user = password_form.save()

                update_session_auth_hash(
                    request,
                    user,
                )

                messages.success(
                    request,
                    "Lozinka je uspješno promijenjena.",
                )

                return redirect(
                    f"{reverse('accounts:settings')}?tab=profile"
                )


        # ==========================================
        # NOTIFICATIONS
        # ==========================================

        elif action == "notifications":

            active_tab = "notifications"

            notification_form = (
                NotificationSettingsForm(
                    request.POST,
                    instance=notification_settings,
                )
            )

            if notification_form.is_valid():

                notification_form.save()

                messages.success(
                    request,
                    "Postavke obavijesti uspješno su spremljene.",
                )

                return redirect(
                    f"{reverse('accounts:settings')}?tab=notifications"
                )


        # ==========================================
        # NOTIFICATIONS
        # ==========================================

        elif action == "notifications":

            active_tab = "notifications"

            notification_form = (
                NotificationSettingsForm(
                    request.POST,
                    instance=notification_settings,
                )
            )


            if notification_form.is_valid():

                notification_form.save()

                messages.success(
                    request,
                    "Postavke obavijesti uspješno su spremljene.",
                )

                return redirect(
                    f"{reverse('accounts:settings')}?tab=notifications"
                )


    # ==============================================
    # CONTEXT
    # ==============================================

    context = {
        "active_tab": active_tab,

        "profile_form": profile_form,
        "password_form": password_form,
        "notification_form": notification_form,
    }


    return render(
        request,
        "accounts/settings.html",
        context,
    )    