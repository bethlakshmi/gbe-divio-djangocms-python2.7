from django.forms import (
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
    volunteer_type = ModelChoiceField(
        queryset=AvailableInterest.objects.filter(visible=True),
        required=False)
    type = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Volunteer")

    class Meta:
        model = GenericEvent
        fields = ['e_title',
                  'volunteer_type',
                  'max_volunteer',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'type',
                  ]
        hidden_fields = ['opp_event_id', 'e_description']
