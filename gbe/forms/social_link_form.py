from django.forms import (
    CharField,
    HiddenInput,
    ImageField,
    inlineformset_factory,
    IntegerField,
    ModelForm,
    Textarea,
)
from gbe.models import (
    Performer,
    SocialLink,
)


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
        widgets = {'order': HiddenInput(attrs={'class':'drag_change'})}

SocialLinkFormSet = inlineformset_factory(Performer,
                                          SocialLink,
                                          form=SocialLinkForm,
                                          max_num=5,
                                          extra=5)
