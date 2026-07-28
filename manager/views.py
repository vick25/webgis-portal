from django.shortcuts import render, redirect
from .forms import GeoshpForm
from .models import Project


def index(request):
    return render(request, "manager/home.html")


def dashboard(request):
    return render(request, "manager/dashboard.html")


def map_view(request):
    # The map obtains its catalogue and selected GeoJSON lazily from the API.
    return render(request, "manager/index.html")


def upload_shp(request):
    if request.method == "POST":
        form = GeoshpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("file_list")
    else:
        form = GeoshpForm()
    return render(request, "manager/uploadShp.html", {"form": form})


def file_list(request):
    from .models import Geoshp

    files = Geoshp.objects.all()
    return render(request, "manager/file_list.html", {"files": files})
