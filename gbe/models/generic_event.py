from itertools import chain
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
)
from gbe.models import (
    AvailableInterest,
    Event,
)
from scheduler.models import EventContainer
from gbetext import (
    calendar_for_event,
    event_options,
)
from ticketing.functions import get_tickets


class GenericEvent (Event):
    '''
    Any event except for a show or a class
    '''
    type = CharField(max_length=128,
                     choices=event_options,
                     blank=False,
                     default="Special")
    volunteer_type = ForeignKey(AvailableInterest,
                                on_delete=CASCADE,
                                blank=True,
                                null=True)

    def __str__(self):
        return self.e_title

    @property
    def event_type(self):
        return self.type

    # tickets that apply to generic events are:
    #   - any ticket that applies to "most" iff this is not a master class
    #   - any ticket that links this event specifically
    # but for all tickets - iff the ticket is active
    #
    def get_tickets(self):
        if self.type in ["Special", "Drop-In"]:
            return get_tickets(self, most=True)
        else:
            return get_tickets(self)

    @property
    def calendar_type(self):
        return calendar_for_event[self.type]

    class Meta:
        app_label = "gbe"
