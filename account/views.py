from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Register View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account created for {username}. You can now log in."
            )
            return redirect("login")
        # If the form is not valid, the 'form' object (with errors) will be passed to the template.
    else:
        form = CustomUserCreationForm()  # Initialize an empty form for GET requests.
    return render(request, "account/register.html", {"form": form})


# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect(
            "manager_index"
        )  # Redirect authenticated users to the index template view.
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("map_view")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "account/login.html")


# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")
