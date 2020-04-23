from model_utils.managers import InheritanceManager
from django.db.models import (
    CharField,
    DurationField,
    TextField,
    AutoField,
    ForeignKey,
)
from scheduler.models import EventItem
from gbe.models import (
    Conference,
    Room
)
from gbetext import calendar_for_event


class Event(EventItem):
    '''
    Event is the base class for any scheduled happening at the expo.
    Events fall broadly into "shows" and "classes". Classes break down
    further into master classes, panels, workshops, etc. Shows are not
    biddable (though the Acts comprising them are) , but classes arise
    from participant bids.
    '''
    objects = InheritanceManager()
    e_title = CharField(max_length=128)
    e_description = TextField()            # public-facing description
    blurb = TextField(blank=True)        # short description
    duration = DurationField()
    notes = TextField(blank=True)  # internal notes about this event
    event_id = AutoField(primary_key=True)
    e_conference = ForeignKey(
        Conference,
        related_name="e_conference_set",
        blank=True,
        null=True)
    default_location = ForeignKey(Room,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return self.e_title

    @classmethod
    def get_all_events(cls, conference):
        events = cls.objects.filter(
            e_conference=conference,
            visible=True).select_subclasses()
        return [event for event in events if
                getattr(event, 'accepted', 3) == 3 and
                getattr(event, 'type', 'X') not in ('Volunteer',
                                                    'Rehearsal Slot',
                                                    'Staff Area')]

    @property
    def event_type(self):
        return self.__class__.__name__

    @property
    def sched_duration(self):
        return self.duration

    @property
    def calendar_type(self):
        return calendar_for_event[self.__class__.__name__]

    @property
    def is_current(self):
        return self.e_conference.status == "upcoming"

    class Meta:
        ordering = ['e_title']
        app_label = "gbe"
