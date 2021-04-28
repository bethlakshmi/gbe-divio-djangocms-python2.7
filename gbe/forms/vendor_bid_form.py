from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    HiddenInput,
    ImageField,
    ModelForm,
    MultipleChoiceField,
    Textarea,
)
from gbe.models import Vendor
from gbe_forms_text import (
    vendor_help_texts,
    vendor_labels,
    vendor_schedule_options,
)
from gbe.expoformfields import FriendlyURLInput
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from django.contrib.auth.models import User


class VendorBidForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    help_times = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=vendor_schedule_options,
        required=False,
        label=vendor_labels['help_times'])

    def __init__(self, *args, **kwargs):
        super(VendorBidForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['upload_img'] = ImageField(
                help_text=vendor_help_texts['upload_img'],
                label=vendor_labels['upload_img'],
                initial=kwargs.get('instance').img,
                required=False,
            )

    class Meta:
        model = Vendor
        fields = ['business',
                  'want_help',
                  'help_description',
                  'help_times',
                  ]
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {'accepted': HiddenInput(),
                   'submitted': HiddenInput(),
                   }
