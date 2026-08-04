from django.shortcuts import render, redirect
from .forms import GeoshpForm
from .models import Project
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "manager/home.html")


@login_required
def dashboard(request):
    return render(request, "manager/dashboard.html")


def map_view(request):
    # The map obtains its catalogue and selected GeoJSON lazily from the API.
    return render(request, "manager/index.html")


@login_required
def upload_shp(request):
    if request.method == "POST":
        form = GeoshpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("file_list")
    else:
        form = GeoshpForm()
    return render(request, "manager/uploadShp.html", {"form": form})


@login_required
def file_list(request):
    from .models import Geoshp

    files = Geoshp.objects.all()
    return render(request, "manager/file_list.html", {"files": files})
