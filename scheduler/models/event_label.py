from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    Model,
)
from scheduler.models import Event


class EventLabel (Model):
    '''
    A decorator allowing free-entry "tags" on allocations
    '''
    text = CharField(default='', max_length=200)
    event = ForeignKey(Event, on_delete=CASCADE)

    class Meta:
        app_label = "scheduler"
        unique_together = (('text', 'event'), )
