
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .validator import phone
from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["phone_number", "full_name"]

    def clean_phone_number(self):
        number = self.cleaned_data["phone_number"]
        phone(number)
        return number

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "phone_number",
            "full_name",
            "password",
            "is_active",
            "is_admin",
        ]


class UserLoginForm(forms.Form):

    phone_number = forms.CharField(
        label="Phone number",
        validators=[phone],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Phone number",
            "autocomplete": "tel",
            "dir": "ltr",
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "autocomplete": "current-password",
        })
    )


class RegisterForm(forms.Form):

    full_name = forms.CharField(
        max_length=100,
        label="Full name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your name",
            "autocomplete": "name",
        })
    )

    phone_number = forms.CharField(
        label="Phone number",
        validators=[phone],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Phone number",
            "autocomplete": "tel",
            "dir": "ltr",
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "new-password",
        })
    )

    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "new-password",
        })
    )

    def clean_phone_number(self):
        number = self.cleaned_data["phone_number"]

        if User.objects.filter(phone_number=number).exists():
            raise ValidationError("This phone number is already registered.")

        return number

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error("password2", "Passwords don't match.")

        return cleaned_data


class CheckOtpForm(forms.Form):

    code = forms.CharField(
        label="Verification code",
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter verification code",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "dir": "ltr",
        })
    )



class CreateProfileForm(forms.Form):

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    fathers_name = forms.CharField(max_length=100)
    national_code = forms.CharField(max_length=100)

    image = forms.ImageField(required=False)


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["full_name", "image"]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Display name",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "image-input",
                "accept": "image/*",
            }),
        }
