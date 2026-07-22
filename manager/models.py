from django.contrib.gis.db import models
import os, re, shutil, tempfile, zipfile
from pathlib import Path, PurePosixPath
from django.contrib import auth
import geopandas as gpd
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# from pg.pg import Pg

# db = Pg(
#     dbname=f"{os.getenv('DB_NAME')}",
#     user=f"{os.getenv('DB_USER')}",
#     password=f"{os.getenv('DB_PASSWORD')}",
#     host=f"{os.getenv('DB_HOST')}",
#     port=f"{os.getenv('DB_PORT')}",
# )


def _normalize_table_name(name):
    normalized = re.sub(r"[^a-zA-Z0-9_]", "_", name).strip("_").lower()
    return normalized or "geoshp"


def extract_single_shapefile(zip_path, destination):
    """Safely unpack one conventional shapefile set and return its .shp path.

    Uploads are user-controlled, so zip member names must be checked before
    extraction to prevent a path-traversal archive from writing outside the
    temporary import directory.
    """
    destination = Path(destination).resolve()
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            member_path = PurePosixPath(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValidationError("ZIP contains an unsafe file path.")
            target = (destination / Path(*member_path.parts)).resolve()
            if not str(target).startswith(str(destination) + os.sep) and target != destination:
                raise ValidationError("ZIP contains an unsafe file path.")
        archive.extractall(destination)

    shp_files = list(destination.rglob("*.shp"))
    if len(shp_files) != 1:
        raise ValidationError("ZIP must contain exactly one .shp file.")

    shp_path = shp_files[0]
    missing = [suffix for suffix in (".dbf", ".shx") if not shp_path.with_suffix(suffix).exists()]
    if missing:
        raise ValidationError(f"Shapefile is missing required companion file(s): {', '.join(missing)}.")
    return str(shp_path)


# Persist the shapefile file as a postgis table
def persist_file(geoshp_instance):
    file_path = geoshp_instance.file.path

    if not file_path.lower().endswith(".zip"):
        raise ValidationError("Upload a ZIP shapefile.")

    if not os.path.exists(file_path):
        raise ValidationError("Uploaded file was not found.")

    temp_dir = tempfile.mkdtemp()

    try:
        shp_path = extract_single_shapefile(file_path, temp_dir)

        # Read shapefile with geopandas
        gdf = gpd.read_file(shp_path)

        # Reproject to WGS 84 (SRID 4326) for standardized storage
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        features_to_create = []

        # Convert geometry to WKT for Django parsing
        # and convert all attributes into a single JSON properties dictionary
        for _, row in gdf.iterrows():
            # Get geometry as a standard WKT string
            wkt_geom = row["geometry"].wkt

            # Extract row attributes excluding geometry
            attributes = row.drop("geometry").to_dict()

            # Convert python types that aren't JSON serializable (like datetime, numpy, etc.)
            clean_attributes = {}
            for k, v in attributes.items():
                if hasattr(v, "isoformat"):  # Handle dates
                    clean_attributes[k] = v.isoformat()
                elif type(v).__name__.startswith("int") or type(v).__name__.startswith(
                    "float"
                ):  # Handle numpy types
                    clean_attributes[k] = v.item() if hasattr(v, "item") else v
                else:
                    clean_attributes[k] = str(v)

            # Instatiate ShapefileFeature model
            feature_obj = ShapefileFeature(
                geoshp=geoshp_instance, geom=wkt_geom, properties=clean_attributes
            )
            features_to_create.append(feature_obj)

        # Fast bulk-creation of all features
        ShapefileFeature.objects.bulk_create(features_to_create)

    except Exception as e:
        raise ValidationError(f"Import failed: {e}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# Create your models here.
class Geoshp(models.Model):
    name = models.CharField(
        max_length=150, unique=True, help_text="Name of the shapefile"
    )
    description = models.TextField(blank=True, help_text="Description of the shapefile")
    file = models.FileField(
        unique=True, upload_to="shapefiles/%Y/%m/%d", help_text="Upload a ZIP shapefile"
    )
    uploaded_date = models.DateField(auto_now_add=True)
    project = models.ForeignKey(
        "Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geoshp_layers",
    )

    def __str__(self):
        return f"{self.name}"


# This is the single, persistent table that will hold ALL geometries from ALL shapefiles
class ShapefileFeature(models.Model):
    # Link back to the parent shapefile upload metadata record
    geoshp = models.ForeignKey(
        Geoshp, on_delete=models.CASCADE, related_name="features"
    )
    # Store geometry generically
    geom = models.GeometryField(srid=4326)
    # Store all custom shapefile attributes as key-values
    properties = models.JSONField(default=dict)

    def __str__(self):
        return f"Feature in {self.geoshp.name}"


@receiver(post_save, sender=Geoshp)
def publish_data(sender, instance, created, **kwargs):
    if created and instance.file:
        persist_file(instance)


@receiver(post_delete, sender=Geoshp)
def delete_data(sender, instance, **kwargs):
    pass
    # db.delete_table(instance.name, schema="public")
    # geo.delete_layer(instance.name, f"{os.getenv('DB_HOST')}")


class Project(models.Model):
    name = models.TextField(unique=True, help_text="Name of the project")
    sigle = models.CharField(
        max_length=20, unique=True, help_text="Sigle of the project"
    )
    description = models.TextField(blank=True, help_text="Description of the project")
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
