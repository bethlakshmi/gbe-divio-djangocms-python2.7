from model_utils.managers import InheritanceManager
from django.db.models import (
    BooleanField,
    CASCADE,
    ForeignKey,
)
from scheduler.models import (
    Event,
    Resource,
    Schedulable,
)


class ResourceAllocation(Schedulable):
    '''
    Joins a particular Resource to a particular Event
    ResourceAllocations get their scheduling data from their Event.
    '''
    objects = InheritanceManager()
    event = ForeignKey(Event,
                       on_delete=CASCADE,
                       related_name="resources_allocated")
    resource = ForeignKey(Resource,
                          on_delete=CASCADE,
                          related_name="allocations")
    default = BooleanField(default=False)
