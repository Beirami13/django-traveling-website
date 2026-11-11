
import secrets

from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import (
    UserLoginForm,
    RegisterForm,
    CheckOtpForm,
    UserEditForm,
)

from .models import OTP, User


class UserLogin(View):

    def get(self, request):
        form = UserLoginForm()

        return render(
            request,
            "account/login.html",
            {"form": form},
        )

    def post(self, request):

        form = UserLoginForm(request.POST)

        if form.is_valid():

            cd = form.cleaned_data

            user = authenticate(
                request,
                phone_number=cd["phone_number"],
                password=cd["password"],
            )

            if user is not None:

                login(request, user)

                return redirect("index")

            form.add_error(
                None,
                "Phone number or password is incorrect."
            )

        return render(
            request,
            "account/login.html",
            {"form": form},
        )


class UserRegister(View):

    def get(self, request):

        form = RegisterForm()

        return render(
            request,
            "account/register.html",
            {"form": form},
        )

    def post(self, request):

        form = RegisterForm(request.POST)

        if form.is_valid():

            cd = form.cleaned_data

            OTP.objects.filter(
                phone_number=cd["phone_number"]
            ).delete()

            rand_code = secrets.randbelow(9000) + 1000
            token = str(uuid4())

            OTP.objects.create(
                phone_number=cd["phone_number"],
                code=rand_code,
                token=token,
                expires_at=timezone.now() + timedelta(minutes=2),
            )

            request.session["register_data"] = {
                "phone_number": cd["phone_number"],
                "full_name": cd["full_name"],
                "password": make_password(cd["password"]),
            }

            request.session["otp_token"] = token

            # TODO: Send OTP through SMS provider.
            # Development only: inspect the code in the server console.
            print("OTP:", rand_code)

            return redirect(
                reverse("account:check_otp") + f"?token={token}"
            )

        return render(
            request,
            "account/register.html",
            {"form": form},
        )


class CheckOtpView(View):

    def get(self, request):

        form = CheckOtpForm()
        token = request.GET.get("token")

        if not token or token != request.session.get("otp_token"):
            form.add_error(None, "Invalid or expired verification session.")

        return render(
            request,
            "account/checkCode.html",
            {
                "form": form,
                "token": token,
            },
        )

    def post(self, request):

        token = request.POST.get("token")

        form = CheckOtpForm(request.POST)

        if not token or token != request.session.get("otp_token"):

            form.add_error(None, "Invalid verification token.")

            return render(
                request,
                "account/checkCode.html",
                {"form": form, "token": token},
            )

        if form.is_valid():

            cd = form.cleaned_data

            otp_obj = OTP.objects.filter(
                code=cd["code"],
                token=token,
            ).first()

            if otp_obj is None:

                form.add_error(
                    "code",
                    "The verification code is incorrect."
                )

            elif otp_obj.is_expired():

                otp_obj.delete()

                form.add_error(
                    "code",
                    "The verification code has expired."
                )

            else:

                data = request.session.get("register_data")

                if (
                    not data
                    or data["phone_number"] != otp_obj.phone_number
                ):

                    form.add_error(
                        None,
                        "Registration data not found. Please register again."
                    )

                else:

                    user = User.objects.filter(
                        phone_number=data["phone_number"]
                    ).first()

                    if user is None:

                        user = User(
                            phone_number=data["phone_number"],
                            full_name=data["full_name"],
                        )

                        # Password was already hashed before entering session.
                        user.password = data["password"]
                        user.save()

                    else:

                        form.add_error(
                            None,
                            "This phone number is already registered."
                        )

                        return render(
                            request,
                            "account/checkCode.html",
                            {"form": form, "token": token},
                        )

                    otp_obj.delete()

                    request.session.pop("register_data", None)
                    request.session.pop("otp_token", None)

                    login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )

                    return redirect("index")

        return render(
            request,
            "account/checkCode.html",
            {
                "form": form,
                "token": token,
            },
        )


@login_required(login_url="account:login")
def edit_profile(request):

    user = request.user

    if request.method == "POST":

        user_form = UserEditForm(
            request.POST,
            request.FILES,
            instance=user,
        )

        if user_form.is_valid():

            user_form.save()

            return redirect("account:edit")

    else:

        user_form = UserEditForm(instance=user)

    return render(
        request,
        "account/settings.html",
        {
            "user_form": user_form,
        },
    )


@login_required(login_url="account:login")
def UserLogout(request):

    if request.method == "POST":

        logout(request)

        return redirect("index")

    return redirect("index")
