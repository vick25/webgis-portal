from rest_framework_gis.serializers import GeoFeatureModelSerializer
from manager.models import ShapefileFeature
from rest_framework import serializers


class ShapefileFeatureSerializer(GeoFeatureModelSerializer):
    geoshp = serializers.StringRelatedField(source="geoshp.name", read_only=True)

    class Meta:
        model = ShapefileFeature
        geo_field = "geom"
        fields = ("geoshp", "geom", "properties")
        id_field = False
