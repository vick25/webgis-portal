from django.contrib.gis import admin
from .models import Geoshp, Project, ShapefileFeature
from leaflet.admin import LeafletGeoAdmin


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sigle",
        "description",
        "creator",
        "created_at",
        "updated_at",
    )
    list_filter = ("creator", "created_at", "updated_at")
    search_fields = ("name", "sigle")


admin.site.register(Project, ProjectAdmin)


class FeatureInline(admin.TabularInline):
    model = ShapefileFeature
    fields = ("geom", "properties")
    readonly_fields = ("geom", "properties")
    extra = 0
    can_delete = True


class GeoshpAdmin(LeafletGeoAdmin):
    date_hierarchy = "uploaded_date"
    list_display = ("name", "project", "file", "uploaded_date")
    list_filter = ("project", "uploaded_date")
    search_fields = ("name",)
    inlines = [FeatureInline]  # Inlines nested perfectly under Leaflet view


admin.site.register(Geoshp, GeoshpAdmin)


@admin.register(ShapefileFeature)
class FeatureAdmin(LeafletGeoAdmin):
    list_display = ("id", "geoshp", "get_properties_summary")
    list_filter = ("geoshp",)

    gis_widget_kwargs = {
        "attrs": {
            "default_zoom": 12,
            "default_lon": 0.0,
            "default_lat": 0.0,
        }
    }

    # Custom helper to safely truncate dynamic JSON properties in the grid view
    def get_properties_summary(self, obj):
        props_str = str(obj.properties)
        return props_str[:100] + "..." if len(props_str) > 100 else props_str

    get_properties_summary.short_description = "Attributes"
