from django.urls import path
from .views import file_list, upload_shp

urlpatterns = [
    path("", upload_shp, name="upload_file"),
    path("files/", file_list, name="file_list"),
]
