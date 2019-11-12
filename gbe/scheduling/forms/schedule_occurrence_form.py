from django.forms import (
    ChoiceField,
    FloatField,
    Form,
    HiddenInput,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import (
    ConferenceDay,
    Room
)
from gbe.functions import (
    get_conference_days,
    get_current_conference
)
from datetime import time
from gbe_forms_text import schedule_occurrence_labels
from settings import (
    GBE_DATE_FORMAT,
    GBE_TIME_FORMAT
)


time_start = 8 * 60
time_stop = 24 * 60
conference_times = [(time(mins/60, mins % 60),
                     time(mins/60, mins % 60).strftime(GBE_TIME_FORMAT))
                    for mins in range(time_start, time_stop, 30)]


class DayChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.day.strftime(GBE_DATE_FORMAT)


class ScheduleOccurrenceForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    day = DayChoiceField(queryset=ConferenceDay.objects.none(),
                         empty_label=None,
                         required=True)
    time = ChoiceField(choices=conference_times, required=True)
    duration = FloatField(min_value=0.5,
                          max_value=12,
                          required=True,
                          label=schedule_occurrence_labels['duration'])
    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    max_volunteer = IntegerField(required=True, initial=0)
    occurrence_id = IntegerField(required=False, widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        open_to_public = None
        if 'conference' in kwargs:
            conference = kwargs.pop('conference')
        else:
            conference = get_current_conference()
        if 'open_to_public' in kwargs:
            open_to_public = kwargs.pop('open_to_public')
        super(ScheduleOccurrenceForm, self).__init__(*args, **kwargs)
        self.fields['day'].queryset = get_conference_days(
            conference,
            open_to_public)
        self.fields['location'].queryset = Room.objects.filter(
            conference=conference)
