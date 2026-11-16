from django import forms
from django.contrib.auth import authenticate

from .models import User, normalize_phone, phone_validator

REQUIRED = "ეს ველი აუცილებელია."


class _PhoneMixin:
    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone"))
        phone_validator(phone)
        taken = User.objects.filter(phone=phone)
        if getattr(self, "instance", None) is not None and self.instance.pk:
            taken = taken.exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError("ამ ნომრით ანგარიში უკვე არსებობს.")
        return phone


class RegisterForm(_PhoneMixin, forms.ModelForm):
    phone = forms.CharField(label="ტელეფონი", max_length=30, error_messages={"required": REQUIRED})
    password = forms.CharField(label="პაროლი", min_length=6, max_length=128,
                               error_messages={"min_length": "პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან.",
                                               "required": REQUIRED})

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email"]
        error_messages = {"email": {"invalid": "შეიყვანეთ სწორი ელფოსტის მისამართი."}}

    def save(self, commit=True):
        return User.objects.create_user(
            phone=self.cleaned_data["phone"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
        )


class LoginForm(forms.Form):
    phone = forms.CharField(label="ტელეფონი", error_messages={"required": REQUIRED})
    password = forms.CharField(label="პაროლი", error_messages={"required": REQUIRED})

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        data = super().clean()
        if data.get("phone") and data.get("password"):
            self.user = authenticate(self.request, username=normalize_phone(data["phone"]), password=data["password"])
            if self.user is None:
                raise forms.ValidationError("ტელეფონის ნომერი ან პაროლი არასწორია.")
        return data


class ProfileForm(_PhoneMixin, forms.ModelForm):
    phone = forms.CharField(label="ტელეფონი", max_length=30, error_messages={"required": REQUIRED})

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]
        error_messages = {"email": {"invalid": "შეიყვანეთ სწორი ელფოსტის მისამართი."}}


class PasswordForm(forms.Form):
    current_password = forms.CharField(label="მიმდინარე პაროლი", error_messages={"required": REQUIRED})
    new_password = forms.CharField(label="ახალი პაროლი", min_length=6, max_length=128,
                                   error_messages={"min_length": "პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან.",
                                                   "required": REQUIRED})

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        value = self.cleaned_data["current_password"]
        if not self.user.check_password(value):
            raise forms.ValidationError("მიმდინარე პაროლი არასწორია.")
        return value


def flatten_errors(form):
    out = []
    for field, errors in form.errors.items():
        label = "" if field == "__all__" else f"{form.fields[field].label or field}: "
        out.extend(f"{label}{e}" for e in errors)
    return out
