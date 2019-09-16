from django.forms import (
    ModelForm,
)
from gbe.models import StageInfo
from gbe.expoformfields import DurationFormField
from gbe_forms_text import (
    act_help_texts,
    prop_labels,
)
from django.core.exceptions import ValidationError


class StageInfoForm(ModelForm):
    form_title = "Stage Info"
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(required=False,
                                     help_text=act_help_texts['act_duration'])

    class Meta:
        model = StageInfo
        labels = prop_labels
        help_texts = act_help_texts
        fields = '__all__'


class StageInfoSubmitForm(StageInfoForm):

    def clean(self):
        # run the parent validation first
        cleaned_data = super(StageInfoSubmitForm, self).clean()
        # doing is_complete doesn't work, that executes the pre-existing
        # instance, not the current data

        if not (self.cleaned_data['set_props'] or
                self.cleaned_data['clear_props'] or
                self.cleaned_data['cue_props'] or
                self.cleaned_data['confirm']):
            raise ValidationError(
                '''Incomplete Prop Info - please either check of whether props
                must set, cleaned up or provided on cue, or confirm that no
                props or set pieces are needed.''',
                code='invalid')

        return cleaned_data
