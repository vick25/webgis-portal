from django.urls import path
from .views import file_list, upload_shp, index

urlpatterns = [
    path("", index, name="manager_index"),
    path("upload/", upload_shp, name="upload_shp"),
    path("files/", file_list, name="file_list"),
]
