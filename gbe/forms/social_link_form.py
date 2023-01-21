from django.forms import (
    ChoiceField,
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
    social_network = ChoiceField(
        choices=([('', '(pick an option)'), ] + SocialLink.social_options),
                 required=False,
                 label='')

    def clean(self):
        cleaned_data = super(SocialLinkForm, self).clean()
        if 'social_network' in cleaned_data:
            if cleaned_data['social_network'] in SocialLink.link_template:
                if not cleaned_data['username']:
                    self.add_error('username', "This field is required.")
            elif len(cleaned_data['social_network']) > 0:
                if not cleaned_data['link']:
                    self.add_error('link', "This field is required.")
        return cleaned_data

    class Meta:
        model = SocialLink
        fields = ['social_network',
                  'link',
                  'username',
                  'order',
                  ]
        widgets = {'order': HiddenInput(attrs={'class':'drag_change'}),
                   'link': URLInput(
                        attrs={'placeholder': 'http://',
                               'style': "width: 98%;box-sizing:border-box"}),
                   'username': TextInput(
                        attrs={'placeholder': 'yourusername'})}
        labels = {'link': '',
                  'username': ''}

SocialLinkFormSet = inlineformset_factory(Performer,
                                          SocialLink,
                                          form=SocialLinkForm,
                                          max_num=5,
                                          extra=5)
