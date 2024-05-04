from django import forms

from apps.web.models import SiteUsers


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = SiteUsers
        fields = ["useremail"]
        widgets = {
            "useremail": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "id": "email",
                    "placeholder": "Emailingiz",
                }
            ),
        }
