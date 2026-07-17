from django import forms
from .models import Geoshp, Project


class GeoshpForm(forms.ModelForm):
    project = Project.objects.all()

    class Meta:
        model = Geoshp
        fields = ("name", "description", "file", "project")
