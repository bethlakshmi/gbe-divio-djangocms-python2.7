from django.forms import (
    BooleanField,
    CharField,
    HiddenInput,
)
from gbe.scheduling.forms import ScheduleBasicForm


class VolunteerOpportunityForm(ScheduleBasicForm):
    approval = BooleanField(initial=False, required=False)
    event_style = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Volunteer")

    class Meta:
        fields = ['title',
                  'max_volunteer',
                  'approval',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'event_style',
                  'opp_sched_id',
                  ]
