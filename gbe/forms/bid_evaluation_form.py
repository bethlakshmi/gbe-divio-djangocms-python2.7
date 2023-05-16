from django.forms import (
    ModelForm,
    HiddenInput,
)
from gbe.models import BidEvaluation


class BidEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = BidEvaluation
        fields = '__all__'
        widgets = {'evaluator': HiddenInput(),
                   'bid': HiddenInput()}
