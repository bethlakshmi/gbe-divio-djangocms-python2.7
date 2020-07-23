from django.db.models import (
    CASCADE,
    ForeignKey,
    Model,
    OneToOneField,
)
from scheduler.models import Event


class EventContainer(Model):
    '''
    Another decorator. Links one Event to another. Used to link
    a volunteer shift (Generic Event) to a Show (or other conf event)
    '''
    parent_event = ForeignKey(Event,
                              on_delete=CASCADE,
                              related_name='contained_events')
    child_event = OneToOneField(Event, 
                                on_delete=CASCADE,
                                related_name='container_event')
