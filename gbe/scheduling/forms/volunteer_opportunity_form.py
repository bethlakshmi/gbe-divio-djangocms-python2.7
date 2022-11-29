from django.forms import BooleanField
from gbe.scheduling.forms import ScheduleBasicForm


class VolunteerOpportunityForm(ScheduleBasicForm):
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
                  'opp_sched_id',
                  ]
