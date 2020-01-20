from django.forms import (
    BooleanField,
    CharField,
    HiddenInput,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import (
    AvailableInterest,
    GenericEvent,
)
from gbe.scheduling.forms import ScheduleBasicForm


class VolunteerOpportunityForm(ScheduleBasicForm):
    opp_event_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    type = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Volunteer")
    approval = BooleanField(initial=False, required=False)

    class Meta:
        model = GenericEvent
        fields = ['e_title',
                  'max_volunteer',
                  'approval',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'type',
                  ]
        hidden_fields = ['opp_event_id', 'e_description']
