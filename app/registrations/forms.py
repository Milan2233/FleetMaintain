from django import forms

from .models import RegistrationInspection


class RegistrationInspectionForm(forms.ModelForm):

    class Meta:
        model = RegistrationInspection

        fields = (
            "vehicle",
            "record_type",
            "date",
            "valid_until",
            "provider",
            "mileage",
            "working_hours",
            "cost",
            "note",
        )

        labels = {
            "vehicle": "Vozilo / stroj",
            "record_type": "Vrsta zapisa",
            "date": "Datum",
            "valid_until": "Vrijedi do",
            "provider": "Stanica / pružatelj usluge",
            "mileage": "Kilometraža",
            "working_hours": "Radni sati",
            "cost": "Trošak",
            "note": "Napomena",
        }

        widgets = {

            "vehicle": forms.Select(),

            "record_type": forms.Select(),

            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "valid_until": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "provider": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Npr. Stanica za tehnički pregled Rijeka"
                    ),
                }
            ),

            "mileage": forms.NumberInput(
                attrs={
                    "placeholder": "Npr. 125000",
                    "min": "0",
                    "step": "1",
                }
            ),

            "working_hours": forms.NumberInput(
                attrs={
                    "placeholder": "Npr. 4250.5",
                    "min": "0",
                    "step": "0.1",
                }
            ),

            "cost": forms.NumberInput(
                attrs={
                    "placeholder": "Npr. 420.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "note": forms.Textarea(
                attrs={
                    "placeholder": (
                        "Unesite dodatne informacije..."
                    ),
                    "rows": 5,
                }
            ),
        }


    # ==============================================
    # INITIALIZATION
    # ==============================================

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        if user is not None:

            self.fields["vehicle"].queryset = (
                self.fields["vehicle"]
                .queryset
                .filter(user=user)
                .order_by("name")
            )


    # ==============================================
    # VALIDATION
    # ==============================================

    def clean(self):

        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        valid_until = cleaned_data.get(
            "valid_until"
        )

        if (
            date
            and valid_until
            and valid_until < date
        ):
            self.add_error(
                "valid_until",
                (
                    "Datum isteka ne može biti "
                    "prije datuma registracije "
                    "ili tehničkog pregleda."
                ),
            )

        return cleaned_data