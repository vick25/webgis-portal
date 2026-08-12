from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import logout

from manager.models import Geoshp, Project, ShapefileFeature

from .serializers import (
    GeoshpSerializer,
    LayerFeatureSerializer,
    ProjectSerializer,
    RegistrationSerializer,
    LoginSerializer,
)


class ApiPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class ProjectListView(generics.ListAPIView):
    """Paginated project catalogue, with each project's available layers."""

    serializer_class = ProjectSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        layer_queryset = Geoshp.objects.annotate(
            feature_count=Count("features")
        ).order_by("name")
        return Project.objects.prefetch_related(
            Prefetch("geoshp_layers", queryset=layer_queryset)
        ).order_by("name")


class GeoshpListView(generics.ListAPIView):
    """Paginated layer-management list. Filter with ?project=<id> or ?unassigned=true."""

    serializer_class = GeoshpSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        queryset = (
            Geoshp.objects.select_related("project")
            .annotate(feature_count=Count("features"))
            .order_by("name")
        )
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if self.request.query_params.get("unassigned", "").lower() == "true":
            queryset = queryset.filter(project__isnull=True)
        return queryset


class LayerGeoJSONView(generics.GenericAPIView):
    """Return all features for exactly one selected layer as a GeoJSON collection."""

    serializer_class = LayerFeatureSerializer

    def get(self, request, pk):
        layer = get_object_or_404(Geoshp, pk=pk)
        features = layer.features.only("id", "geom", "properties")
        serializer = self.get_serializer(features, many=True)
        return Response(
            {
                "type": "FeatureCollection",
                "name": layer.name,
                "features": serializer.data,
            }
        )


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": f"User {user.username}, registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return Response(
                {
                    "message": f"Login successful for user {user.username}.",
                    "user_id": user.id,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
