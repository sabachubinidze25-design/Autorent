from django import forms

from .models import Car


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["brand", "model", "year", "price", "capacity", "fuel_capacity",
                  "transmission", "city", "image1", "image2", "image3"]
        error_messages = {
            f: {"invalid_choice": "აირჩიეთ მნიშვნელობა სიიდან."} for f in ("brand", "transmission", "city")
        }


class RentForm(forms.Form):
    start_date = forms.DateField(label="დაწყების თარიღი",
                                 error_messages={"required": "აირჩიეთ დაწყების თარიღი.",
                                                 "invalid": "დაწყების თარიღი არასწორია."})
    end_date = forms.DateField(label="დასრულების თარიღი",
                               error_messages={"required": "აირჩიეთ დასრულების თარიღი.",
                                               "invalid": "დასრულების თარიღი არასწორია."})
