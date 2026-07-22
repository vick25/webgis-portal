from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from manager.models import Geoshp, Project, ShapefileFeature


class LayerApiTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="map-user",
            email="map@example.com",
            password="safe-test-password",
        )
        self.project = Project.objects.create(
            name="Forest monitoring", sigle="FM", creator=user
        )
        self.layer = Geoshp.objects.create(
            name="Observation sites",
            # Model save does not run form validation; keep the file empty so
            # the post-save importer is not invoked in this API-only test.
            file="",
            project=self.project,
        )
        # The upload signal only imports when an actual file exists; features
        # are created explicitly here to focus the test on the API contract.
        ShapefileFeature.objects.create(
            geoshp=self.layer,
            geom=Point(15.0, -3.0, srid=4326),
            properties={"site_name": "Lomela", "count": 3},
        )

    def test_layer_geojson_is_a_flat_feature_collection(self):
        response = self.client.get(reverse("layer-geojson", args=[self.layer.pk]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["type"], "FeatureCollection")
        self.assertEqual(payload["features"][0]["geometry"]["type"], "Point")
        self.assertEqual(payload["features"][0]["properties"]["site_name"], "Lomela")
        self.assertNotIn("properties", payload["features"][0]["properties"])

    def test_project_catalog_exposes_its_layer_and_geojson_link(self):
        response = self.client.get(reverse("project-list"))

        self.assertEqual(response.status_code, 200)
        layer = response.json()["results"][0]["layers"][0]
        self.assertEqual(layer["feature_count"], 1)
        self.assertIn(reverse("layer-geojson", args=[self.layer.pk]), layer["geojson_url"])
