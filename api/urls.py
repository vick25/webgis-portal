from django.urls import path
from .views import GeoShpListView

urlpatterns = [
    path("geoshp/", GeoShpListView.as_view(), name="geoshp-list"),
]
