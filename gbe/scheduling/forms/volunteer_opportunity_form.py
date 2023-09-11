from django.forms import (
    BooleanField,
    CharField,
    HiddenInput,
    ModelChoiceField,
)
from gbe.scheduling.forms import ScheduleBasicForm
from dal import autocomplete
from django.urls import reverse_lazy
from scheduler.models import Event


class VolunteerOpportunityForm(ScheduleBasicForm):
    approval = BooleanField(initial=False, required=False)
    event_style = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Volunteer")
    peer = ModelChoiceField(
        queryset=Event.objects.filter(event_style="Volunteer"),
        required=False,
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy('volunteer-autocomplete',
                             urlconf="gbe.scheduling.urls")))

    class Meta:
        fields = ['title',
                  'max_volunteer',
                  'approval',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'event_style',
                  'peer',
                  'opp_sched_id',
                  ]
