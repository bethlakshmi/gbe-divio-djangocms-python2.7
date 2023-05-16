from django.forms import (
    ChoiceField,
    HiddenInput,
    ModelForm,
    RadioSelect,
)
from gbe.models import FlexibleEvaluation
from django.db.models.fields import BLANK_CHOICE_DASH


class FlexibleEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super(FlexibleEvaluationForm, self).__init__(*args, **kwargs)
        choice_set = [(i, "") for i in range(-1, 6)]
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            self.fields['ranking'] = ChoiceField(
                label=initial['category'].category,
                help_text=initial['category'].help_text,
                required=False,
                widget=RadioSelect,
                choices=choice_set)

    def clean_ranking(self):
        if not self.cleaned_data['ranking'] or len(
                self.cleaned_data['ranking']) == 0:
            return -1
        else:
            return self.cleaned_data['ranking']

    class Meta:
        model = FlexibleEvaluation
        fields = ['ranking',
                  'category',
                  'evaluator_acct',
                  'bid']
        widgets = {'category': HiddenInput(),
                   'evaluator_acct': HiddenInput(),
                   'bid': HiddenInput(), }
