from django.forms import (
    ChoiceField,
    FloatField,
    ModelForm,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import (
    Event,
    Room
)
from gbe.functions import get_current_conference
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


class ScheduleBasicForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    day = ChoiceField(choices=['No Days Specified'])
    time = ChoiceField(choices=conference_times)
    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    max_volunteer = IntegerField(required=True)
    duration = FloatField(min_value=0.5,
                          max_value=12,
                          required=True)
    class Meta:
        model = Event
        fields = ['e_title',
                  'e_description',
                  'duration',
                  'max_volunteer',
                  'day',
                  'time',
                  'location',
                  ]

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            conference = kwargs['instance'].e_conference
            if 'initial' in kwargs and 'duration' not in kwargs['initial']:
                kwargs['initial']['duration'] = float(
                    kwargs['instance'].duration.total_seconds())/3600
        else:
            conference = kwargs.pop('conference')
        super(ScheduleBasicForm, self).__init__(*args, **kwargs)
        self.fields['day'] = ModelChoiceField(
            queryset=conference.conferenceday_set.all())
        self.fields['location'] = ModelChoiceField(
            queryset=Room.objects.filter(conferences=conference))

    def clean_duration(self):
        data = timedelta(minutes=self.cleaned_data['duration']*60)
        return data
