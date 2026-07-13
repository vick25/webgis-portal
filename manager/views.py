from django.shortcuts import render, redirect
from .forms import GeoshpForm


def upload_shp(request):
    if request.method == "POST":
        form = GeoshpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("file_list")
    else:
        form = GeoshpForm()
    return render(request, "manager/uploadShp.html", {"form": form})

    form = GeoshpForm(request.GET)

    if form.is_valid() and form.cleaned_data["file_input"]:
        file_input = form.cleaned_data["file_input"]
        uploadedFile = request.FILES["file_input"]

    return render(
        request,
        "manager/uploadShp.html",
        {"form": form},
    )


def file_list(request):
    from .models import Geoshp

    files = Geoshp.objects.all()
    return render(request, "manager/file_list.html", {"files": files})


# def book_search(request):
#     search_text = request.GET.get("search", "")
#     form = SearchForm(request.GET)
#     books = set()

#     if form.is_valid() and form.cleaned_data["search"]:
#         search = form.cleaned_data["search"]
#         search_in = form.cleaned_data.get("search_in") or "title"
#         if search_in == "title":
#             books = Book.objects.filter(title__icontains=search)
#         else:
#             fname_contributors = Contributor.objects.filter(
#                 first_names__icontains=search
#             )

#             for contributor in fname_contributors:
#                 for book in contributor.book_set.all():
#                     books.add(book)

#             lname_contributors = Contributor.objects.filter(
#                 last_names__icontains=search
#             )

#             for contributor in lname_contributors:
#                 for book in contributor.book_set.all():
#                     books.add(book)

#     return render(
#         request,
#         "reviews/search-results.html",
#         {"form": form, "search_text": search_text, "books": books},
#     )
