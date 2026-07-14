from django.contrib.gis import admin

from .models import Geoshp, Project

# Register your models here.


class GeoshpAdmin(admin.GISModelAdmin):
    date_hierarchy = "uploaded_date"
    list_display = ("project", "name", "name_db", "file", "uploaded_date")
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
