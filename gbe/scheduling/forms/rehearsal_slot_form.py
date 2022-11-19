from django.forms import (
    CharField,
    HiddenInput,
    IntegerField,
    NumberInput,
)
from gbe.scheduling.forms import ScheduleBasicForm


class RehearsalSlotForm(ScheduleBasicForm):
    opp_event_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    event_style = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Rehearsal Slot")
    current_acts = IntegerField(
        widget=NumberInput(attrs={'readonly': 'readonly'}),
        required=False)

    class Meta:
        fields = ['title',
                  'current_acts',
                  'max_volunteer',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'event_style',
                  ]
