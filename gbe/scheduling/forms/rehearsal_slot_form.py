from django.forms import (
    CharField,
    HiddenInput,
    IntegerField,
    NumberInput,
)
from gbe.models import GenericEvent
from gbe.scheduling.forms import ScheduleBasicForm


class RehearsalSlotForm(ScheduleBasicForm):
    opp_event_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    type = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Rehearsal Slot")
    current_acts = IntegerField(
        widget=NumberInput(attrs={'readonly': 'readonly'}),
        required=False)

    class Meta:
        model = GenericEvent
        fields = ['e_title',
                  'current_acts',
                  'max_volunteer',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'type',
                  ]
