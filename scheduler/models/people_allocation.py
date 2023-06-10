from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    TextField,
    Model,
)
from scheduler.models import (
    Event,
    People,
)
from gbetext import role_options


class PeopleAllocation(Model):
    '''
    Joins a particular Resource to a particular Event
    ResourceAllocations get their scheduling data from their Event.
    '''
    event = ForeignKey(Event,
                       on_delete=CASCADE)
    people = ForeignKey(People,
                        on_delete=CASCADE)
    role = CharField(max_length=50, choices=role_options, blank=True)
    label = TextField(blank=True)
