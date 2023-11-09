from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.forms import (
    ChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    RadioSelect,
)
from gbe.models import (
    Class,
    ClassLabel,
    UserMessage,
)
from gbe_forms_text import (
    acceptance_help_texts,
    acceptance_labels,
    difficulty_default_text,

)
from gbetext import difficulty_options
from dal import autocomplete


class ClassStateChangeForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    difficulty = ChoiceField(
        widget=RadioSelect,
        choices=difficulty_options,
        required=False)
    labels = ModelMultipleChoiceField(
        required=False,
        queryset=ClassLabel.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
            url=reverse_lazy('classlabel-autocomplete', urlconf='gbe.urls')))

    def __init__(self, *args, **kwargs):
        super(ClassStateChangeForm, self).__init__(*args, **kwargs)
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
        fields = ['accepted',
                  'labels',
                  'difficulty']
        required = ['accepted']
        labels = acceptance_labels
        help_texts = acceptance_help_texts
