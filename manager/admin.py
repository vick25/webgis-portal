from django.contrib.gis import admin
from .models import Geoshp, Project, ShapefileFeature
from leaflet.admin import LeafletGeoAdmin


class GeoshpAdmin(LeafletGeoAdmin):
    date_hierarchy = "uploaded_date"
    list_display = ("name", "project", "file", "uploaded_date")
    list_filter = ("project", "uploaded_date")


admin.site.register(Geoshp, GeoshpAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sigle",
        "description",
        "creator__username",
        "created_at",
        "updated_at",
    )
    list_filter = ("creator__username", "created_at", "updated_at")
    search_fields = ("name", "sigle")


admin.site.register(Project, ProjectAdmin)


class FeatureInline(admin.TabularInline):
    model = ShapefileFeature
    # Limit fields shown in inline view to prevent slow page loads with massive layers
    fields = ("geom", "properties")
    readonly_fields = ("geom", "properties")
    extra = 0
    can_delete = True


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = ("name", "geom_type", "uploaded_at")
    search_fields = ("name",)
    inlines = [FeatureInline]


@admin.register(ShapefileFeature)
class FeatureAdmin(admin.GISModelAdmin):
    list_display = ("id", "geoshp", "get_properties_summary")
    list_filter = ("geoshp",)

    # Show openstreetmap interface to inspect geometries in detail
    gis_widget_kwargs = {
        "attrs": {
            "default_zoom": 12,
            "default_lon": 0.0,
            "default_lat": 0.0,
        }
    }

    # Custom helper to show a snippet of the JSON properties in the list view
    def get_properties_summary(self, obj):
        return (
            str(obj.properties)[:100] + "..."
            if len(str(obj.properties)) > 100
            else str(obj.properties)
        )

    get_properties_summary.short_description = "Attributes"
