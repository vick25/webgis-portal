from django.shortcuts import render
from manager.models import ShapefileFeature, Project, Geoshp
from .serializers import ShapefileFeatureSerializer, ProjectSerializer, GeoshpSerializer
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class ShapefileFeatureView(generics.ListAPIView):
    queryset = ShapefileFeature.objects.all()
    serializer_class = ShapefileFeatureSerializer
    # filter_backends = [
    #     DjangoFilterBackend,
    # ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = (
        "geoshp__name",
        "geoshp__project__name",
        # "properties",
    )


class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class GeoshpListView(generics.ListAPIView):
    queryset = Geoshp.objects.all()
    serializer_class = GeoshpSerializer
