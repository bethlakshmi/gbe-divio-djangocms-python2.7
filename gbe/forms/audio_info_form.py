from django.forms import (
    ModelForm,
)
from gbe.models import AudioInfo
from gbe.expoformfields import DurationFormField
from gbe_forms_text import (
    act_help_texts,
    act_bid_labels,
)
from django.core.exceptions import ValidationError


class AudioInfoForm(ModelForm):
    form_title = "Audio Info"
    required_css_class = 'required'
    error_css_class = 'error'
    track_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )

    class Meta:
        model = AudioInfo
        fields = '__all__'


class AudioInfoSubmitForm(AudioInfoForm):

    def clean(self):
        # run the parent validation first
        cleaned_data = super(AudioInfoSubmitForm, self).clean()

        # doing is_complete doesn't work, that executes the pre-existing
        # instance, not the current data
        if not (
                (self.cleaned_data['track_title'] and
                 self.cleaned_data['track_artist'] and
                 'track_duration' in self.cleaned_data
                 ) or
                self.cleaned_data['confirm_no_music']):
            raise ValidationError(
                ('Incomplete Audio Info - please either provide Track Title,'
                 'Artist and Duration, or confirm that there is no music.'),
                code='invalid')
        return cleaned_data
