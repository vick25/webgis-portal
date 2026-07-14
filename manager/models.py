from django.db import models
import glob, os, re, shutil, tempfile, zipfile
from django.contrib import auth
import geopandas as gpd
from django.core.exceptions import ValidationError
from geoalchemy2 import Geometry
from sqlalchemy import create_engine
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from pg.pg import Pg

conn_str = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)
db = Pg(
    dbname=f"{os.getenv('DB_NAME')}",
    user=f"{os.getenv('DB_USER')}:",
    password=f"{os.getenv('DB_PASSWORD')}",
    host=f"{os.getenv('DB_HOST')}",
    port=f"{os.getenv('DB_PORT')}",
)


def _normalize_table_name(name):
    normalized = re.sub(r"[^a-zA-Z0-9_]", "_", name).strip("_").lower()
    return normalized or "geoshp"


# Persist the shapefile file as a postgis table
def persist_file(file_path, table_name):
    if not file_path.lower().endswith(".zip"):
        raise ValidationError("Upload a ZIP shapefile.")

    if not os.path.exists(file_path):
        raise ValidationError("Uploaded file was not found.")

    temp_dir = tempfile.mkdtemp()

    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        shp_files = glob.glob(
            os.path.join(temp_dir, "**", "*.shp"),
            recursive=True,
        )

        if not shp_files:
            raise ValidationError("No shapefile found inside ZIP.")

        shp_path = shp_files[0]

        gdf = gpd.read_file(shp_path)

        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)

        gdf = gdf.rename_geometry("geom")

        table_name = _normalize_table_name(table_name)

        engine = create_engine(conn_str)

        gdf.to_postgis(
            name=table_name,
            con=engine,
            schema="public",
            if_exists="replace",
            index=True,
            dtype={"geom": Geometry("MULTIPOLYGON", srid=4326)},
        )

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
    uploaded_date = models.DateField(
        auto_now_add=True, verbose_name="Date the ZIP file was uploaded."
    )
    project = models.ForeignKey(
        "Project", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def name_db(self):
        nameDb = _normalize_table_name(self.name)
        return nameDb


@receiver(post_save, sender=Geoshp)
def publish_data(sender, instance, created, **kwargs):
    if not instance.file:
        return

    persist_file(instance.file.path, instance.name)


@receiver(post_delete, sender=Geoshp)
def delete_data(sender, instance, **kwargs):
    db.delete_table(instance.name, schema="public")
    # geo.delete_layer(instance.name, "wwfdb")


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
