from pathlib import Path

from django import forms

from .models import VehicleDocument


class VehicleDocumentForm(forms.ModelForm):

    # ==============================================
    # FILE SETTINGS
    # ==============================================

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


    class Meta:

        model = VehicleDocument

        fields = (
            "vehicle",
            "name",
            "document_type",
            "file",
            "issue_date",
            "valid_until",
            "description",
        )

        labels = {
            "vehicle": "Vozilo / stroj",
            "name": "Naziv dokumenta",
            "document_type": "Vrsta dokumenta",
            "file": "Datoteka",
            "issue_date": "Datum izdavanja",
            "valid_until": "Vrijedi do",
            "description": "Opis",
        }

        widgets = {

            "vehicle": forms.Select(),

            "name": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Npr. Polica osiguranja 2026."
                    ),
                }
            ),

            "document_type": forms.Select(),

            "file": forms.FileInput(
                attrs={
                    "accept": (
                        ".pdf,.jpg,.jpeg,.png,.webp"
                    ),
                }
            ),

            "issue_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "valid_until": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": (
                        "Unesite dodatne informacije "
                        "o dokumentu..."
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
    # FILE VALIDATION
    # ==============================================

    def clean_file(self):

        uploaded_file = self.cleaned_data.get(
            "file"
        )

        if not uploaded_file:
            return uploaded_file


        extension = (
            Path(uploaded_file.name)
            .suffix
            .lower()
        )


        if extension not in self.ALLOWED_EXTENSIONS:

            raise forms.ValidationError(
                (
                    "Podržani formati datoteka su "
                    "PDF, JPG, JPEG, PNG i WEBP."
                )
            )


        if uploaded_file.size > self.MAX_FILE_SIZE:

            raise forms.ValidationError(
                (
                    "Maksimalna veličina "
                    "datoteke je 10 MB."
                )
            )


        return uploaded_file


    # ==============================================
    # DATE VALIDATION
    # ==============================================

    def clean(self):

        cleaned_data = super().clean()

        issue_date = cleaned_data.get(
            "issue_date"
        )

        valid_until = cleaned_data.get(
            "valid_until"
        )


        if (
            issue_date
            and valid_until
            and valid_until < issue_date
        ):

            self.add_error(
                "valid_until",
                (
                    "Datum isteka ne može biti "
                    "prije datuma izdavanja."
                ),
            )


        return cleaned_data