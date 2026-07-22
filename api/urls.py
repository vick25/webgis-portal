from django.urls import path
from .views import ShapefileFeatureView, ProjectListView, GeoshpListView

urlpatterns = [
    path("features/", ShapefileFeatureView.as_view(), name="feature-list"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("geoshps/", GeoshpListView.as_view(), name="geoshp-list"),
]
