from django.forms import (
    BooleanField,
    CharField,
    HiddenInput,
    IntegerField,
    ModelChoiceField,
)
from gbe.scheduling.forms import ScheduleBasicForm


class VolunteerOpportunityForm(ScheduleBasicForm):
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    event_style = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Volunteer")
    approval = BooleanField(initial=False, required=False)

    class Meta:
        fields = ['title',
                  'max_volunteer',
                  'approval',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'event_style',
                  ]
