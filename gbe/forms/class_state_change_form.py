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
)
from gbe_forms_text import (
    acceptance_help_texts,
    acceptance_labels,
)
from gbetext import difficulty_options
from gbe.functions import dynamic_difficulty_options
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
        self.fields['difficulty'].choices = dynamic_difficulty_options()

    class Meta:
        model = Class
        fields = ['accepted',
                  'labels',
                  'difficulty']
        required = ['accepted']
        labels = acceptance_labels
        help_texts = acceptance_help_texts
