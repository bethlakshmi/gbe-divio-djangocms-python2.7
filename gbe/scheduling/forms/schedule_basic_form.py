from django.forms import (
    CharField,
    ChoiceField,
    FloatField,
    Form,
    HiddenInput,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import Room
from datetime import (
  timedelta,
  time,
)
from settings import GBE_TIME_FORMAT


time_start = 8 * 60
time_stop = 24 * 60
conference_times = [(time(int(mins/60), mins % 60),
                     time(int(mins/60), mins % 60).strftime(GBE_TIME_FORMAT))
                    for mins in range(time_start, time_stop, 30)]


class ScheduleBasicForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    title = CharField(required=True, max_length=128)
    current_acts = IntegerField(
        widget=HiddenInput(),
        required=False)
    max_volunteer = IntegerField(required=True)
    duration = FloatField(min_value=0.5,
                          max_value=12,
                          required=True)
    day = ChoiceField(choices=['No Days Specified'])
    time = ChoiceField(choices=conference_times)
    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    event_style = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Rehearsal Slot")

    def __init__(self, *args, **kwargs):
        conference = kwargs.pop('conference')
        super(ScheduleBasicForm, self).__init__(*args, **kwargs)
        self.fields['day'] = ModelChoiceField(
            queryset=conference.conferenceday_set.all())
        self.fields['location'] = ModelChoiceField(
            queryset=Room.objects.filter(conferences=conference))

    def clean_duration(self):
        data = timedelta(minutes=self.cleaned_data['duration']*60)
        return data
