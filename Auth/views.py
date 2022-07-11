from django.shortcuts import *
from .forms import *
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as dlogin, logout as dlogout
from django.contrib import messages


def signup(request):
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account Created! ")
            return redirect("login")
    return render(request, "Auth/signup.html", context={"form": form})


def login(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                dlogin(request, user)
                return redirect("home")
    return render(request, "Auth/login.html", context={"form": form})


@login_required
def logout(request):
    dlogout(request)
    return redirect("home")


@login_required
def change_profile(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(instance=profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated Successfully!")
            form = ProfileForm(instance=profile)
    context = {"profile": profile, "form": form}
    return render(request, "Auth/change_profile.html", context)
