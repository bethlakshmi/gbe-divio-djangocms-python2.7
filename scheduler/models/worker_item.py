from model_utils.managers import InheritanceManager
from scheduler.models import ResourceItem


class WorkerItem(ResourceItem):
    '''
    Payload object for a person as resource (staff/volunteer/teacher)
    '''
    objects = InheritanceManager()

    @property
    def as_subtype(self):
        '''
        REFACTOR!!  Scheduler should't know anything about GBE.
        Returns this item as its underlying conference type.
        (either Performer or Profile)
        '''
        from django.core.exceptions import ObjectDoesNotExist
        try:
            p = self.performer
        except ObjectDoesNotExist:
            p = self.profile
        return p

    @property
    def is_active(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).is_active

    @property
    def describe(self):
        child = WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id)
        if child.__class__.__name__ == "WorkerItem":
            return "Worker Item (no child_event)"
        return child.__class__.__name__ + ":  " + child.describe

    def __str__(self):
        return str(self.describe)

    def get_bookings(self, role, conference=None):
        '''
        Returns the events for which this Worker is booked as "role".
        should remain focused on the upward connection of resource
        allocations, and avoid being sub class specific
        '''
        from scheduler.models import Event

        events = Event.objects.filter(
            resources_allocated__resource__worker___item=self,
            resources_allocated__resource__worker__role=role)
        if conference:
            events = events.filter(
                eventlabel__text=conference.conference_slug)
        return events
