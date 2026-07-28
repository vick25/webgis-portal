from django.urls import path
from .views import dashboard, file_list, index, map_view, upload_shp

urlpatterns = [
    path("", index, name="manager_index"),
    path("dashboard/", dashboard, name="manager_dashboard"),
    path("map/", map_view, name="map_view"),
    path("upload/", upload_shp, name="upload_shp"),
    path("files/", file_list, name="file_list"),
]
