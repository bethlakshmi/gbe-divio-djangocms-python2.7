from django.forms import (
    IntegerField,
    NumberInput,
)
from gbe.scheduling.forms import ScheduleBasicForm


class RehearsalSlotForm(ScheduleBasicForm):

    current_acts = IntegerField(
        widget=NumberInput(attrs={'readonly': 'readonly'}),
        required=False)

    class Meta:
        fields = ['title',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'event_style',
                  'opp_sched_id',
                  'current_acts',
                  'max_volunteer',
                  ]
