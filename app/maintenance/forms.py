from django import forms

from .models import Maintenance


class MaintenanceForm(forms.ModelForm):

    class Meta:
        model = Maintenance

        fields = (
            "vehicle",
            "title",
            "maintenance_type",
            "status",
            "scheduled_date",
            "completed_date",
            "service_provider",
            "mileage",
            "working_hours",
            "cost",
            "description",
            "next_service_date",
            "next_service_mileage",
            "next_service_working_hours",
        )

        labels = {
            "vehicle": "Vozilo / stroj",
            "title": "Naziv održavanja",
            "maintenance_type": "Vrsta održavanja",
            "status": "Status",
            "scheduled_date": "Planirani datum",
            "completed_date": "Datum završetka",
            "service_provider": "Servis / izvođač",
            "mileage": "Kilometraža",
            "working_hours": "Radni sati",
            "cost": "Trošak",
            "description": "Opis",
            "next_service_date": "Datum sljedećeg servisa",
            "next_service_mileage": "Kilometraža sljedećeg servisa",
            "next_service_working_hours": "Radni sati sljedećeg servisa",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "npr. Redovni servis na 120.000 km",
                }
            ),

            "scheduled_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "completed_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "service_provider": forms.TextInput(
                attrs={
                    "placeholder": "npr. Auto servis Rijeka",
                }
            ),

            "mileage": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 120350",
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

            "cost": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 284.50",
                    "min": 0,
                    "step": "0.01",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "Opišite izvršene ili planirane radove...",
                    "rows": 5,
                }
            ),

            "next_service_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "next_service_mileage": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 135000",
                    "min": 0,
                }
            ),

            "next_service_working_hours": forms.NumberInput(
                attrs={
                    "placeholder": "npr. 4750",
                    "min": 0,
                    "step": "0.1",
                }
            ),
        }


    # ==================================================
    # USER VEHICLES
    # ==================================================

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        if user is not None:

            self.fields["vehicle"].queryset = (
                self.fields["vehicle"]
                .queryset
                .filter(user=user)
            )


    # ==================================================
    # FORM VALIDATION
    # ==================================================

    def clean(self):

        cleaned_data = super().clean()

        status = cleaned_data.get("status")

        scheduled_date = cleaned_data.get(
            "scheduled_date"
        )

        completed_date = cleaned_data.get(
            "completed_date"
        )

        mileage = cleaned_data.get(
            "mileage"
        )

        next_service_mileage = cleaned_data.get(
            "next_service_mileage"
        )

        working_hours = cleaned_data.get(
            "working_hours"
        )

        next_service_working_hours = cleaned_data.get(
            "next_service_working_hours"
        )


        # ==============================================
        # COMPLETED MAINTENANCE
        # ==============================================

        if (
            status == Maintenance.Status.COMPLETED
            and completed_date is None
        ):
            self.add_error(
                "completed_date",
                "Za završeno održavanje unesite datum završetka.",
            )


        # ==============================================
        # DATE ORDER
        # ==============================================

        if (
            scheduled_date
            and completed_date
            and completed_date < scheduled_date
        ):
            self.add_error(
                "completed_date",
                "Datum završetka ne može biti prije planiranog datuma.",
            )


        # ==============================================
        # NEXT SERVICE MILEAGE
        # ==============================================

        if (
            mileage is not None
            and next_service_mileage is not None
            and next_service_mileage <= mileage
        ):
            self.add_error(
                "next_service_mileage",
                "Kilometraža sljedećeg servisa mora biti veća od trenutačne kilometraže.",
            )


        # ==============================================
        # NEXT SERVICE WORKING HOURS
        # ==============================================

        if (
            working_hours is not None
            and next_service_working_hours is not None
            and next_service_working_hours <= working_hours
        ):
            self.add_error(
                "next_service_working_hours",
                "Radni sati sljedećeg servisa moraju biti veći od trenutačnih radnih sati.",
            )


        return cleaned_data