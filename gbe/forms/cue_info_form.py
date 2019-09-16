from django.forms import (
    HiddenInput,
    ModelForm,
    Textarea,
    TextInput,
)
from gbe.models import CueInfo
from gbe_forms_text import main_cue_header


class CueInfoForm(ModelForm):
    form_title = "Cue List"
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = CueInfo
        widgets = {'techinfo': HiddenInput(),
                   'cue_sequence': TextInput(
                       attrs={'readonly': 'readonly',
                              'size': '1'}),
                   'cue_off_of': Textarea(attrs={'cols': '20',
                                                 'rows': '8'}),
                   'sound_note': Textarea(attrs={'rows': '8'})}
        required = ['wash', 'cyc_color']
        labels = main_cue_header
        cue_off_of_msg = ('Add text if you wish to save information '
                          'for this cue.')
        error_messages = {'cue_off_of': {'required': cue_off_of_msg}}
        fields = '__all__'
