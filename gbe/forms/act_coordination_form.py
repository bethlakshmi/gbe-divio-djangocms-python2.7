from django.forms import (
    CharField,
    DurationField,
    HiddenInput,
    IntegerField,
    ModelForm,
    Textarea,
)
from dal import autocomplete
from gbe.models import Act
from gbe_forms_text import (
    act_help_texts,
    act_bid_labels,
)
from django.urls import reverse_lazy


class ActCoordinationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationField(
        required=False,
        help_text=act_help_texts['act_duration']
    )
    track_artist = CharField(required=False)
    track_title = CharField(required=False)
    b_conference = HiddenInput()
    b_description = CharField(
        required=True,
        label=act_bid_labels['description'],
        help_text=act_help_texts['description'],
        widget=Textarea)

    class Meta:
        model = Act
        fields = [
            'performer',
            'b_title',
            'track_title',
            'track_artist',
            'act_duration',
            'b_description',
            'b_conference']
        labels = act_bid_labels
        help_texts = act_help_texts
        widgets = {
            'b_conference': HiddenInput(),
            'performer': autocomplete.ModelSelect2(
                url=reverse_lazy('coordinator-performer-autocomplete',
                                 urlconf="gbe.urls")),
            }
