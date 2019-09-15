from itertools import chain
from django.db.models import (
    ManyToManyField,
    CharField,
)
from django.conf import settings
from gbe.models import (
    Act,
    Event,
    Persona,
)
from gbetext import cue_options
from ticketing.functions import get_tickets
import os as os


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

    @property
    def schedule_ready(self):
        return True      # shows are always ready for scheduling

    # tickets that apply to shows are:
    #   - any ticket that applies to "most" ("most"= no Master Classes)
    #   - any ticket that links this event specifically
    # but for all tickets - iff the ticket is active
    #
    def get_tickets(self):
        return get_tickets(self, most=True)

    def get_acts(self):
        return self.scheduler_events.first().get_acts()

    def download_path(self):
        path = os.path.join(
            settings.MEDIA_ROOT,
            "uploads",
            "audio",
            "downloads",
            ("%s_%s.tar.gz" %
             (self.e_conference.conference_slug,
              self.e_title.replace(" ", "_").replace("/", "_"))))
        return path

    class Meta:
        app_label = "gbe"
