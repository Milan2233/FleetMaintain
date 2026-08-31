from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import CustomUser, NotificationSettings


User = get_user_model()


# ==================================================
# REGISTRATION FORM
# ==================================================

class RegistrationForm(UserCreationForm):

    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": (
            "Lozinke se ne podudaraju."
        ),
    }

    full_name = forms.CharField(
        label="Ime i prezime",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Unesite ime i prezime",
                "class": "form-control",
            }
        ),
    )

    email = forms.EmailField(
        label="E-mail adresa",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Unesite e-mail adresu",
                "class": "form-control",
            }
        ),
    )

    password1 = forms.CharField(
        label="Lozinka",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Unesite lozinku",
                "class": "form-control",
            }
        ),
    )

    password2 = forms.CharField(
        label="Potvrdite lozinku",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Ponovno unesite lozinku",
                "class": "form-control",
            }
        ),
    )


    class Meta:

        model = CustomUser

        fields = (
            "full_name",
            "email",
            "password1",
            "password2",
        )


    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        full_name = (
            self.cleaned_data["full_name"]
            .strip()
        )

        name_parts = full_name.split(
            maxsplit=1
        )

        user.first_name = name_parts[0]

        user.last_name = (
            name_parts[1]
            if len(name_parts) > 1
            else ""
        )

        # Username se interno koristi samo zbog
        # nasljeđivanja AbstractUser modela.

        user.username = (
            self.cleaned_data["email"]
        )

        user.email = (
            self.cleaned_data["email"]
        )

        if commit:
            user.save()

        return user


# ==================================================
# LOGIN FORM
# ==================================================

class EmailAuthenticationForm(AuthenticationForm):

    error_messages = {
        "invalid_login": (
            "Unesite ispravnu e-mail adresu i lozinku. "
            "Provjerite jeste li podatke unijeli točno."
        ),
        "inactive": (
            "Ovaj korisnički račun nije aktivan."
        ),
    }

    username = forms.EmailField(
        label="E-mail adresa",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Unesite e-mail adresu",
                "class": "form-control",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Lozinka",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Unesite lozinku",
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )


# ==================================================
# PROFILE SETTINGS FORM
# ==================================================

class ProfileSettingsForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Unesite ime",
                    "autocomplete": "given-name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Unesite prezime",
                    "autocomplete": "family-name",
                }
            ),

            "email": forms.EmailInput(),
        }

        labels = {
            "first_name": "Ime",
            "last_name": "Prezime",
            "email": "Email adresa",
        }


    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        # Email korisničkog računa se
        # ne može mijenjati u postavkama.

        self.fields["email"].disabled = True


# ==================================================
# SETTINGS PASSWORD CHANGE FORM
# ==================================================

class SettingsPasswordChangeForm(PasswordChangeForm):

    error_messages = {
        **PasswordChangeForm.error_messages,

        "password_incorrect": (
            "Trenutna lozinka nije ispravna."
        ),

        "password_mismatch": (
            "Nove lozinke se ne podudaraju."
        ),
    }


    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )


        # CURRENT PASSWORD

        self.fields[
            "old_password"
        ].widget.attrs.update(
            {
                "placeholder": "Unesite trenutnu lozinku",
                "autocomplete": "current-password",
            }
        )

        self.fields[
            "old_password"
        ].error_messages[
            "required"
        ] = (
            "Unesite trenutnu lozinku."
        )


        # NEW PASSWORD

        self.fields[
            "new_password1"
        ].widget.attrs.update(
            {
                "placeholder": "Unesite novu lozinku",
                "autocomplete": "new-password",
            }
        )

        self.fields[
            "new_password1"
        ].error_messages[
            "required"
        ] = (
            "Unesite novu lozinku."
        )


        # CONFIRM PASSWORD

        self.fields[
            "new_password2"
        ].widget.attrs.update(
            {
                "placeholder": "Potvrdite novu lozinku",
                "autocomplete": "new-password",
            }
        )

        self.fields[
            "new_password2"
        ].error_messages[
            "required"
        ] = (
            "Potvrdite novu lozinku."
        )

# ==================================================
# NOTIFICATION SETTINGS FORM
# ==================================================

class NotificationSettingsForm(forms.ModelForm):

    class Meta:

        model = NotificationSettings

        fields = [
            "email_enabled",
            "notification_email",
            "remind_30_days",
            "remind_7_days",
            "remind_1_day",
        ]

        widgets = {

            "email_enabled": (
                forms.CheckboxInput()
            ),

            "notification_email": (
                forms.EmailInput(
                    attrs={
                        "placeholder": (
                            "Email adresa za obavijesti"
                        ),
                        "autocomplete": "email",
                    }
                )
            ),

            "remind_30_days": (
                forms.CheckboxInput()
            ),

            "remind_7_days": (
                forms.CheckboxInput()
            ),

            "remind_1_day": (
                forms.CheckboxInput()
            ),
        }