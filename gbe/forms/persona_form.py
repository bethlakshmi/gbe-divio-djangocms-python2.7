from django.forms import (
    CharField,
    HiddenInput,
    ImageField,
    IntegerField,
    ModelForm,
    Textarea,
)
from gbe.models import (
    Bio,
    SocialLink,
)
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
    pronoun_choices,
)
from gbe.expoformfields import FriendlyURLInput
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from django.contrib.auth.models import User
from gbe.forms import (
    ChoiceWithOtherField,
    SocialLinkFormSet,
)


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
    pronouns = ChoiceWithOtherField(
        label=persona_labels['pronouns'],
        choices=pronoun_choices)

    def clean(self):
        cleaned_data = super(PersonaForm, self).clean()
        if 'name' in cleaned_data:
            cleaned_data['name'] = cleaned_data['name'].strip('\'\"')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formset_initial = []
        if 'instance' in kwargs and kwargs.get('instance') is not None:
            self.fields['upload_img'] = ImageField(
                help_text=persona_help_texts['promo_image'],
                label=persona_labels['promo_image'],
                initial=kwargs.get('instance').img,
                required=False,
            )
            for i in range(1, 6):
                if not SocialLink.objects.filter(
                        bio=kwargs.get('instance'), order=i).exists():
                    formset_initial += [{'order': i}]
        else:
            for i in range(1, 6):
                formset_initial += [{'order': i}]

        kwargs['initial'] = formset_initial
        self.formset = SocialLinkFormSet(*args, **kwargs)
        self.link_template = SocialLink.link_template

    def is_valid(self):
        valid = super().is_valid()
        valid = valid and self.formset.is_valid()
        return valid

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
            # on create performer must go first
            performer.save()
            self.formset.instance = performer
            self.formset.save()
            self.save_m2m()
            i = 1
            performer.links.filter(social_network__exact='').delete()
            for link in performer.links.all():
                if link.order != i:
                    link.order = i
                    link.save()
                i = i + 1

        return performer

    class Meta:
        model = Bio
        fields = ['name',
                  'label',
                  'pronouns',
                  'bio',
                  'year_started',
                  'awards',
                  'contact',
                  ]
        help_texts = persona_help_texts
        labels = persona_labels
        widgets = {'contact': HiddenInput(),
                   }
