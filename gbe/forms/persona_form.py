from django.forms import (
    CharField,
    HiddenInput,
    ImageField,
    IntegerField,
    ModelForm,
    Textarea,
)
from gbe.models import Persona
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
)
from gbe.expoformfields import FriendlyURLInput
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from django.contrib.auth.models import User


class PersonaForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    upload_img = ImageField(
        help_text=persona_help_texts['promo_image'],
        label=persona_labels['promo_image'],
        required=False,
    )
    year_started = IntegerField(
        required=True,
        label=persona_labels['year_started'],
        help_text=persona_help_texts['year_started'])
    bio = CharField(
        widget=Textarea(attrs={'id': 'user-tiny-mce'}),
        label=persona_labels['bio'],
        help_text=persona_help_texts['bio'])

    def clean(self):
        cleaned_data = super(PersonaForm, self).clean()
        if 'name' in cleaned_data:
            cleaned_data['name'] = cleaned_data['name'].strip('\'\"')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(PersonaForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs.get('instance') is not None:
            self.fields['upload_img'] = ImageField(
                help_text=persona_help_texts['promo_image'],
                label=persona_labels['promo_image'],
                initial=kwargs.get('instance').img,
                required=False,
            )

    def save(self, commit=True):
        performer = super(PersonaForm, self).save(commit=False)
        if commit and self['upload_img'] and (
                self['upload_img'].value() != performer.img):
            if self['upload_img'].value():
                superuser = User.objects.get(username='admin_img')
                folder, created = Folder.objects.get_or_create(
                    name='Performers')
                img, created = Image.objects.get_or_create(
                    owner=superuser,
                    original_filename=self['upload_img'].value().name,
                    file=self['upload_img'].value(),
                    folder=folder,
                    author="%s" % str(performer.name,),
                )
                img.save()
                performer.img_id = img.pk
            else:
                performer.img = None
        if commit:
            performer.save()
            self.save_m2m()

        return performer

    class Meta:
        model = Persona
        fields = ['name',
                  'label',
                  'homepage',
                  'bio',
                  'year_started',
                  'awards',
                  'performer_profile',
                  'contact',
                  ]
        help_texts = persona_help_texts
        labels = persona_labels
        widgets = {'performer_profile': HiddenInput(),
                   'contact': HiddenInput(),
                   'homepage': FriendlyURLInput,
                   }
