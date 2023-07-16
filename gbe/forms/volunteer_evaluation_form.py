from django.forms import ModelForm
from gbe.models import VolunteerEvaluation


class VolunteerEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = VolunteerEvaluation
        fields = ['vote', 'notes']
        labels = {'vote': 'Recruit for next year?'}
