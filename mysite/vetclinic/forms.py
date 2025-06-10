from django import forms
from .models import Pet, Service


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name",
            "species",
            "breed",
            "gender",
            "date_of_birth",
            "weight_kg",
            "photo",
        ]


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "base_price", "duration_minutes"]
