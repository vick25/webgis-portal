from django.urls import path

from .views import (
    GeoshpListView,
    LayerGeoJSONView,
    ProjectListView,
    RegistrationView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("layers/", GeoshpListView.as_view(), name="layer-list"),
    path("layers/<int:pk>/geojson/", LayerGeoJSONView.as_view(), name="layer-geojson"),
    path("register/", RegistrationView.as_view(), name="api-register"),
    path("login/", LoginView.as_view(), name="api-login"),
    path("logout/", LogoutView.as_view(), name="api-logout"),
]
