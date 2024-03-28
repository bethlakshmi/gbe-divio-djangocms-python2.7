from django.forms import (
    CharField,
    ImageField,
    ModelForm,
    Textarea,
)
from gbe.models import Business
from gbe_forms_text import (
    vendor_help_texts,
    vendor_labels,
)
from gbe.expoformfields import FriendlyURLInput
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from django.contrib.auth.models import User


class BusinessForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    upload_img = ImageField(
        help_text=vendor_help_texts['upload_img'],
        label=vendor_labels['upload_img'],
        required=False,
    )
    description = CharField(
        required=True,
        widget=Textarea(attrs={'id': 'user-tiny-mce'}),
        help_text=vendor_help_texts['description'],
        label=vendor_labels['description'])

    def __init__(self, *args, **kwargs):
        super(BusinessForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs.get('instance') is not None:
            self.fields['upload_img'] = ImageField(
                help_text=vendor_help_texts['upload_img'],
                label=vendor_labels['upload_img'],
                initial=kwargs.get('instance').img,
                required=False,
            )

    def save(self, commit=True):
        business = super(BusinessForm, self).save(commit=False)
        if commit and self['upload_img'] and (
                self.cleaned_data['upload_img'] != business.img):
            if self.cleaned_data['upload_img']:
                superuser = User.objects.get(username='admin_img')
                folder, created = Folder.objects.get_or_create(
                    name='Vendors')
                img, created = Image.objects.get_or_create(
                    owner=superuser,
                    original_filename=self.cleaned_data['upload_img'].name,
                    file=self.cleaned_data['upload_img'],
                    folder=folder,
                    author="%s" % str(business.name,),
                )
                img.save()
                business.img_id = img.pk
            else:
                business.img = None
        if commit:
            business.save()
            self.save_m2m()

        return business

    class Meta:
        model = Business
        fields = ['name',
                  'description',
                  'website',
                  'physical_address',
                  'publish_physical_address',
                  ]
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {'website': FriendlyURLInput}
