from django.urls import path

from .views import GeoshpListView, LayerGeoJSONView, ProjectListView

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("layers/", GeoshpListView.as_view(), name="layer-list"),
    path("layers/<int:pk>/geojson/", LayerGeoJSONView.as_view(), name="layer-geojson"),
]
