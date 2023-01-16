from django.forms import (
    HiddenInput,
    inlineformset_factory,
    ModelForm,
    TextInput,
    URLInput,
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
        widgets = {'order': HiddenInput(attrs={'class':'drag_change'}),
                   'link': URLInput(attrs={'placeholder': 'http://',
                                           'size': 60}),
                   'username': TextInput(attrs={'placeholder': 'yourusername'})}
        labels = {'social_network': '',
                  'link': '',
                  'username': ''}

SocialLinkFormSet = inlineformset_factory(Performer,
                                          SocialLink,
                                          form=SocialLinkForm,
                                          max_num=5,
                                          extra=5)
