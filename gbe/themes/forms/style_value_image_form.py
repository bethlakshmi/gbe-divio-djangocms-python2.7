from django.forms import (
    ClearableFileInput,
    HiddenInput,
    ImageField,
    ModelChoiceField,
    ModelForm,
)
from django.forms.widgets import RadioSelect
from gbe.models import (
    StyleProperty,
    StyleValue,
)
from gbe_forms_text import style_value_help
from filer.models.imagemodels import Image
from django.contrib.auth.models import User
from filer.models.foldermodels import Folder
from django.utils.safestring import mark_safe
from easy_thumbnails.files import get_thumbnailer


class ThumbnailImageField(ModelChoiceField):
    def label_from_instance(self, obj):
        options = {'size': (100, 100), 'crop': False}
        thumb_url = get_thumbnailer(obj).get_thumbnail(options).url
        other_links = "Filename: %s" % (obj.original_filename)
        return mark_safe(
            "<img src='%s' title='%s'/>" % (thumb_url, other_links))


class StyleValueImageForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    style_property = ModelChoiceField(widget=HiddenInput(),
                                      queryset=StyleProperty.objects.all())
    image = ThumbnailImageField(
        widget=RadioSelect(),
        queryset=Image.objects.filter(
            folder__name="Backgrounds").order_by('original_filename'),
        required=False,
        label="Current Image",
        empty_label="No Image",
        blank=True,
        help_text=style_value_help['change_images'])
    add_image = ImageField(
        widget=ClearableFileInput(),
        required=False,
        help_text=style_value_help['add_image'])

    class Meta:
        model = StyleValue
        fields = ['style_property', 'image']

    def save(self, commit=True):
        style_value = super(StyleValueImageForm, self).save(commit=False)
        # need whether or not commit=True for clone, as it will make a new
        # object, so want to consistently set up image.
        if self['add_image'] and self['add_image'].value():
            superuser = User.objects.get(username='admin_img')
            folder, created = Folder.objects.get_or_create(
                name='Backgrounds')
            img, created = Image.objects.get_or_create(
                owner=superuser,
                original_filename=self['add_image'].value().name,
                file=self['add_image'].value(),
                folder=folder,
                author="theme form",
            )
            img.save()
            style_value.image_id = img.pk
        if commit:
            style_value.save()
            self.save_m2m()
        return style_value
