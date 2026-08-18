from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class RegistrationForm(UserCreationForm):
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
        user = super().save(commit=False)

        full_name = self.cleaned_data["full_name"].strip()
        name_parts = full_name.split(maxsplit=1)

        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Username korisnik neće unositi niti koristiti za prijavu.
        # Interno koristimo e-mail kako bismo zadovoljili postojeće
        # username polje AbstractUser modela.
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class EmailAuthenticationForm(AuthenticationForm):
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

class EmailAuthenticationForm(AuthenticationForm):

    error_messages = {
        "invalid_login": (
            "Unesite ispravnu e-mail adresu i lozinku. "
            "Provjerite jeste li podatke unijeli točno."
        ),
        "inactive": "Ovaj korisnički račun nije aktivan.",
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