from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from manager.models import Geoshp, Project, ShapefileFeature

from .serializers import GeoshpSerializer, LayerFeatureSerializer, ProjectSerializer


class ApiPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class ProjectListView(generics.ListAPIView):
    """Paginated project catalogue, with each project's available layers."""

    serializer_class = ProjectSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        layer_queryset = Geoshp.objects.annotate(feature_count=Count("features")).order_by("name")
        return Project.objects.prefetch_related(
            Prefetch("geoshp_layers", queryset=layer_queryset)
        ).order_by("name")


class GeoshpListView(generics.ListAPIView):
    """Paginated layer-management list. Filter with ?project=<id> or ?unassigned=true."""

    serializer_class = GeoshpSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        queryset = Geoshp.objects.select_related("project").annotate(
            feature_count=Count("features")
        ).order_by("name")
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
