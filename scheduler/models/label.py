from django.db.models import (
    CASCADE,
    Model,
    OneToOneField,
    TextField,
)
from scheduler.models import ResourceAllocation


class Label(Model):
    '''
    A decorator allowing free-entry "tags" on allocations
    '''
    text = TextField(default='')
    allocation =OneToOneField(ResourceAllocation, on_delete=CASCADE)
