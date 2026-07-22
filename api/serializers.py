import json

from rest_framework import serializers

from manager.models import Geoshp, Project, ShapefileFeature


class LayerFeatureSerializer(serializers.ModelSerializer):
    """Serialize a database feature as a standard GeoJSON Feature."""

    class Meta:
        model = ShapefileFeature
        fields = ("id", "geom", "properties")

    def to_representation(self, instance):
        # ``GeometryField.geojson`` returns a GeoJSON geometry and avoids the
        # extra, nested ``properties`` member produced by generic serializers.
        return {
            "type": "Feature",
            "id": instance.pk,
            "geometry": json.loads(instance.geom.geojson) if instance.geom else None,
            "properties": instance.properties or {},
        }


class GeoshpSerializer(serializers.ModelSerializer):
    """Small layer payload suitable for project and layer catalogues."""

    feature_count = serializers.IntegerField(read_only=True)
    geojson_url = serializers.HyperlinkedIdentityField(
        view_name="layer-geojson", lookup_field="pk", read_only=True
    )

    class Meta:
        model = Geoshp
        fields = (
            "id",
            "name",
            "description",
            "uploaded_date",
            "project",
            "feature_count",
            "geojson_url",
        )
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    """A project plus the layers that the map panel can render."""

    layers = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("id", "name", "sigle", "description", "created_at", "updated_at", "layers")
        read_only_fields = fields

    def get_layers(self, project):
        layers = project.geoshp_layers.all()
        return GeoshpSerializer(layers, many=True, context=self.context).data
