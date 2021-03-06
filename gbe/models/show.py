from django.db.models import (
    ManyToManyField,
    CharField,
)
from gbe.models import (
    Act,
    Event,
    Persona,
)
from gbetext import cue_options
from ticketing.functions import get_tickets
from scheduler.idd import get_people


class Show (Event):
    '''
    A Show is an Event consisting of a sequence of Acts.
    Future to do: remove acts as field of this class, do acceptance
    and scheduling through scheduler  (post 2015)
    '''
    cue_sheet = CharField(max_length=128,
                          choices=cue_options,
                          blank=False,
                          default="Theater")
    type = "Show"

    def __str__(self):
        return self.e_title

    # tickets that apply to shows are:
    #   - any ticket that applies to "most" ("most"= no Master Classes)
    #   - any ticket that links this event specifically
    # but for all tickets - iff the ticket is active
    #
    def get_tickets(self):
        return get_tickets(self, most=True)

    def get_acts(self):
        acts = []
        response = get_people(parent_event_ids=[self.eventitem_id],
                              roles=["Performer"])
        for performer in response.people:
            act = Act.objects.get(pk=performer.commitment.class_id)
            acts += [act]
        return acts

    class Meta:
        app_label = "gbe"
