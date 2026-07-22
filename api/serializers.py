from rest_framework_gis.serializers import GeoFeatureModelSerializer
from manager.models import ShapefileFeature, Project, Geoshp
from rest_framework import serializers


class ShapefileFeatureSerializer(GeoFeatureModelSerializer):
    geoshp = serializers.StringRelatedField(source="geoshp.name", read_only=True)

    class Meta:
        model = ShapefileFeature
        geo_field = "geom"
        fields = ("geoshp", "geom", "properties")
        id_field = False


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ("creator",)


class GeoshpSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField()

    class Meta:
        model = Geoshp
        fields = "__all__"
