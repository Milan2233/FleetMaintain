from datetime import date

from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle

        fields = (
            "name",
            "vehicle_type",
            "manufacturer",
            "model",
            "production_year",
            "registration_number",
            "vin_serial_number",
            "fuel_type",
            "current_mileage",
            "working_hours",
            "status",
            "note",
            "image",
        )

        labels = {
            "name": "Naziv vozila / stroja",
            "vehicle_type": "Vrsta vozila / stroja",
            "manufacturer": "Proizvođač",
            "model": "Model",
            "production_year": "Godina proizvodnje",
            "registration_number": "Registracijska oznaka",
            "vin_serial_number": "VIN / serijski broj",
            "fuel_type": "Vrsta goriva",
            "current_mileage": "Trenutna kilometraža",
            "working_hours": "Radni sati",
            "status": "Status",
            "note": "Napomena",
            "image": "Slika vozila / stroja",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "npr. VW Transporter",
                }
            ),

            "manufacturer": forms.TextInput(
                attrs={
                    "placeholder": "npr. Volkswagen",
                }
            ),

            "model": forms.TextInput(
                attrs={
                    "placeholder": "npr. Transporter",
                }
            ),

            "production_year": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 2021",
                    "min": 1900,
                }
            ),

            "registration_number": forms.TextInput(
                attrs={
                    "placeholder": "npr. RI-123-AB",
                }
            ),

            "vin_serial_number": forms.TextInput(
                attrs={
                    "placeholder": "VIN ili serijski broj",
                }
            ),

            "current_mileage": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 125000",
                    "min": 0,
                }
            ),

            "working_hours": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 4280.5",
                    "min": 0,
                    "step": "0.1",
                }
            ),

            "note": forms.Textarea(
                attrs={
                    "placeholder": "Dodatne informacije o vozilu ili stroju",
                    "rows": 4,
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
        }


    def clean_production_year(self):
        production_year = self.cleaned_data.get(
            "production_year"
        )

        if production_year is None:
            return production_year

        current_year = date.today().year

        if production_year < 1900:
            raise forms.ValidationError(
                "Godina proizvodnje ne može biti manja od 1900."
            )

        if production_year > current_year + 1:
            raise forms.ValidationError(
                "Unesite ispravnu godinu proizvodnje."
            )

        return production_year