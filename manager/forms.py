from django import forms
from .models import Geoshp, Project


class GeoshpForm(forms.ModelForm):
    project = Project.objects.all()

    class Meta:
        model = Geoshp
        fields = ("name", "description", "file", "project")


# class GeoshpForm(forms.Form):
#     name_input = forms.CharField(required=True, min_length=5)
#     description_input = forms.CharField(required=False)
#     file_input = forms.FileField(required=True)
#     project_input = forms.ChoiceField(
#         required=False, choices=(("project1", "Project 1"), ("project2", "Project 2"))
#     )
