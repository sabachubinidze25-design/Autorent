from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, PasswordForm, ProfileForm, RegisterForm, flatten_errors


def _safe_next(request, value):
    if value and url_has_allowed_host_and_scheme(value, allowed_hosts={request.get_host()}):
        return value
    return ""


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "ანგარიში შეიქმნა. ახლა შეგიძლიათ გაიაროთ ავტორიზაცია.")
            return redirect("login")
        for error in flatten_errors(form):
            messages.error(request, error)
    return render(request, "register.html", {"values": request.POST})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    next_url = _safe_next(request, request.POST.get("next") or request.GET.get("next"))
    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST":
        if form.is_valid():
            login(request, form.user)
            return redirect(next_url or "home")
        for error in flatten_errors(form):
            messages.error(request, error)
    return render(request, "login.html", {"phone": request.POST.get("phone", ""), "next": next_url})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_edit(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    password_form = PasswordForm(user)

    if request.method == "POST":
        if request.POST.get("action") == "password":
            password_form = PasswordForm(user, request.POST)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password"])
                user.save()
                update_session_auth_hash(request, user)  # stay logged in
                messages.success(request, "პაროლი შეიცვალა.")
                return redirect("profile_edit")
            for error in flatten_errors(password_form):
                messages.error(request, error)
        else:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "მონაცემები განახლდა.")
                return redirect("profile_edit")
            for error in flatten_errors(profile_form):
                messages.error(request, error)
            user.refresh_from_db()

    return render(request, "profile_edit.html", {"profile_form": profile_form, "password_form": password_form})
