from django import forms
from .models import Geoshp, Project


class GeoshpForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
    )

    class Meta:
        model = Geoshp
        fields = ("name", "description", "file", "project")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "The file generic name."}),
            "description": forms.Textarea(
                attrs={"placeholder": "A brief description of the file."}
            ),
            "file": forms.FileInput(attrs={"accept": ".zip"}),
        }
