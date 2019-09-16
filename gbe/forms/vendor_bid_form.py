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
from tinymce.widgets import TinyMCE


class VendorBidForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    b_description = CharField(
        required=True,
        widget=TinyMCE(
            attrs={'cols': 80, 'rows': 20},
            mce_attrs={
                'theme_advanced_buttons1': "bold,italic,underline,|," +
                "justifyleft,justifycenter,justifyright,|,bullist,numlist,|," +
                "cut,copy,paste",
                'theme_advanced_buttons2': "",
                'theme_advanced_buttons3': "", }),
        help_text=vendor_help_texts['description'],
        label=vendor_labels['description'])
    help_times = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=vendor_schedule_options,
        required=False,
        label=vendor_labels['help_times'])
    upload_img = ImageField(
        help_text=vendor_help_texts['upload_img'],
        label=vendor_labels['upload_img'],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(VendorBidForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['upload_img'] = ImageField(
                help_text=vendor_help_texts['upload_img'],
                label=vendor_labels['upload_img'],
                initial=kwargs.get('instance').img,
                required=False,
            )

    def save(self, commit=True):
        vendor = super(VendorBidForm, self).save(commit=False)
        if commit and self['upload_img'] and (
                self['upload_img'].value() != vendor.img):
            if self['upload_img'].value():
                superuser = User.objects.get(username='admin_img')
                folder, created = Folder.objects.get_or_create(
                    name='Vendors')
                img, created = Image.objects.get_or_create(
                    owner=superuser,
                    original_filename=self['upload_img'].value().name,
                    file=self['upload_img'].value(),
                    folder=folder,
                    author="%s" % str(vendor.profile),
                )
                img.save()
                vendor.img_id = img.pk
            else:
                vendor.img = None
        if commit:
            vendor.save()

        return vendor

    class Meta:
        model = Vendor
        fields = ['b_title',
                  'b_description',
                  'profile',
                  'website',
                  'physical_address',
                  'publish_physical_address',
                  'want_help',
                  'help_description',
                  'help_times',
                  ]
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {'accepted': HiddenInput(),
                   'submitted': HiddenInput(),
                   'profile': HiddenInput(),
                   'website': FriendlyURLInput,
                   }
