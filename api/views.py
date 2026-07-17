from django.shortcuts import render
from manager.models import ShapefileFeature
from .serializers import ShapefileFeatureSerializer
from rest_framework import generics


class GeoShpListView(generics.ListAPIView):
    queryset = ShapefileFeature.objects.all()
    serializer_class = ShapefileFeatureSerializer
