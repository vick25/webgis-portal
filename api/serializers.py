import json

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from manager.models import Geoshp, Project, ShapefileFeature

User = get_user_model()


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
        fields = (
            "id",
            "name",
            "sigle",
            "description",
            "created_at",
            "updated_at",
            "layers",
        )
        read_only_fields = fields

    def get_layers(self, project):
        layers = project.geoshp_layers.all()
        return GeoshpSerializer(layers, many=True, context=self.context).data


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")

        login(self.context.get("request"), user)
        data["user"] = user
        return data
