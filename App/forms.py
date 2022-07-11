from django import forms
from .models import *


class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ["address", "zip_code", "city", "country"]