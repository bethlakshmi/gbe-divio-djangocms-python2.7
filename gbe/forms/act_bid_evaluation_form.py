from django.forms import (
    ModelForm,
    HiddenInput,
)
from gbe.models import ActBidEvaluation


class ActBidEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = ActBidEvaluation
        fields = ['notes', 'evaluator_acct', 'bid']
        widgets = {'evaluator_acct': HiddenInput(),
                   'bid': HiddenInput()}
