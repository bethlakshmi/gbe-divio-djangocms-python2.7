from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.forms import (
    BooleanField,
    ChoiceField,
    IntegerField,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField,
    RadioSelect,
    SlugField,
    Textarea,
    TextInput,
)
from gbe_forms_text import (
    classbid_help_texts,
    classbid_labels,
    difficulty_default_text,
    event_help_texts,
)
from gbe.models import (
    Class,
    ClassLabel,
    UserMessage,
)
from gbetext import (
    class_options,
    difficulty_options,
)
from dal import autocomplete


class ClassBookingForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)
    submitted = BooleanField(widget=HiddenInput, initial=True)
    type = ChoiceField(choices=class_options)
    difficulty = ChoiceField(
        widget=RadioSelect,
        choices=difficulty_options,
        required=False)
    labels = ModelMultipleChoiceField(
        required=False,
        queryset=ClassLabel.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
            url=reverse_lazy('classlabel-autocomplete', urlconf='gbe.urls')))
    slug = SlugField(help_text=event_help_texts['slug'],
                     required=False)

    def __init__(self, *args, **kwargs):
        super(ClassBookingForm, self).__init__(*args, **kwargs)
        dynamic_difficulty_options = []
        for choice in difficulty_options:
            # keep view hardcoding, because we want to keep consistent
            label_desc, created = UserMessage.objects.get_or_create(
                view="MakeClassView",
                code="%s_DIFFICULTY" % choice[0].upper(),
                defaults={
                    'summary': "%s Difficulty Description" % choice[0],
                    'description': difficulty_default_text[choice[0]]})
            dynamic_difficulty_options += [(
                choice[0],
                mark_safe("<b>%s:</b> %s" % (choice[1],
                                             label_desc.description)))]
        self.fields['difficulty'].choices = dynamic_difficulty_options

    class Meta:
        model = Class
        fields = ['type',
                  'b_title',
                  'b_description',
                  'maximum_enrollment',
                  'fee',
                  'labels',
                  'difficulty',
                  'accepted',
                  'submitted',
                  'id',
                  'slug',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
        widgets = {'b_description': Textarea(attrs={'id': 'admin-tiny-mce'})}
