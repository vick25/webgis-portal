from django.db import models
import glob, os, shutil, tempfile, zipfile
from django.contrib import auth
import geopandas as gpd
from django.core.exceptions import ValidationError
from geoalchemy2 import Geometry
from sqlalchemy import create_engine
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

conn_str = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)


# Create your models here.
class Geoshp(models.Model):
    name = models.CharField(
        max_length=150, unique=True, help_text="Name of the shapefile"
    )
    description = models.TextField(blank=True, help_text="Description of the shapefile")
    file = models.FileField(
        upload_to="shapefiles/%Y/%m/%d", help_text="Upload a ZIP shapefile"
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
        super().save(*args, **kwargs)

        # Validate the uploaded file
        file_path = self.file.path

        if not file_path.endswith(".zip"):
            raise ValidationError("Upload a ZIP shapefile.")

        temp_dir = tempfile.mkdtemp()

        # Extract the shapefile and create a postgis table
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

            table_name = self.name.lower().replace(" ", "_").replace("-", "_")

            engine = create_engine(conn_str)

            gdf.to_postgis(
                name=table_name,
                con=engine,
                schema="public",
                if_exists="replace",
                index=True,
                dtype={"geometry": Geometry("MULTIPOLYGON", srid=4326)},
            )

        except Exception as e:
            raise ValidationError(f"Import failed: {e}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@receiver(post_save, sender=Geoshp)
def publish_data(sender, instance, created, **kwargs):
    print({"Geoshp": "********ok***********"})


@receiver(post_delete, sender=Geoshp)
def delete_data(sender, instance, **kwargs):
    pass
    # db.delete_table(instance.name, schema='public')
    # geo.delete_layer(instance.name, "wwfdb")


class Project(models.Model):
    name = models.TextField(unique=True, help_text="Name of the project")
    sigle = models.CharField(
        max_length=20, unique=True, help_text="Sigle of the project"
    )
    description = models.TextField(blank=True, help_text="Description of the project")
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
