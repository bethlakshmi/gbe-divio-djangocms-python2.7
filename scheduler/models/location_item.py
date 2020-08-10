from model_utils.managers import InheritanceManager
from scheduler.models import ResourceItem


class LocationItem(ResourceItem):
    '''
    "Payload" object for a Location
    '''
    objects = InheritanceManager()

    @property
    def as_subtype(self):
        return self.room

    @property
    def get_bookings(self):
        '''
        Returns the events for which this LocationItem is booked.
        should remain focused on the upward connection of resource
        allocations, and avoid being subclass specific
        '''
        from scheduler.models import Event

        events = Event.objects.filter(
            resources_allocated__resource__location___item=self
        ).order_by(
            'starttime')
        return events

    @property
    def describe(self):
        return LocationItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).name

    def __str__(self):
        return str(self.describe)
