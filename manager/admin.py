from django.contrib.gis import admin

from .models import Geoshp

# Register your models here.


class GeoshpAdmin(admin.GISModelAdmin):
    date_hierarchy = "uploaded_date"
    list_display = ("project", "name", "name_db", "file", "uploaded_date")
    list_filter = ("project", "uploaded_date")


admin.site.register(Geoshp, GeoshpAdmin)
