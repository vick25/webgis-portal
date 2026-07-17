from django.shortcuts import render, redirect
from .forms import GeoshpForm


def index(request):
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
