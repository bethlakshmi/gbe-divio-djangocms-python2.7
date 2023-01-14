from django.forms import (
    CharField,
    HiddenInput,
    ImageField,
    IntegerField,
    ModelForm,
    Textarea,
)
from gbe.models import SocialLink


class SocialLinkForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = SocialLink
        fields = ['social_network',
                  'link',
                  'username',
                  'order',
                  ]
