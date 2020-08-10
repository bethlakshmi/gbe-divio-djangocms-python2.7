from model_utils.managers import InheritanceManager
from django.db.models import (
    AutoField,
    BooleanField,
    Model,
)
from scheduler.models import Worker


class EventItem (Model):
    '''
    The payload for an event (ie, a class, act, show, or generic event)
    The EventItem must not impose any DB usage on its implementing model
    classes.
    '''
    objects = InheritanceManager()
    eventitem_id = AutoField(primary_key=True)
    visible = BooleanField(default=True)

    def child(self):
        return EventItem.objects.get_subclass(eventitem_id=self.eventitem_id)

    def get_conference(self):
        return self.child().e_conference

    # DEPRECATE - when scheduling refactored
    def roles(self, roles=['Teacher',
                           'Panelist',
                           'Moderator',
                           'Staff Lead']):
        from scheduler.models import EventContainer
        try:
            container = EventContainer.objects.filter(
                child_event__eventitem=self).first()
            people = Worker.objects.filter(
                (Q(allocations__event__eventitem=self) &
                 Q(role__in=roles)) |
                (Q(allocations__event=container.parent_event) &
                 Q(role__in=roles))).distinct().order_by(
                'role', '_item')
        except:
            people = Worker.objects.filter(
                allocations__event__eventitem=self,
                role__in=roles
            ).distinct().order_by('role', '_item')
        return people

    @property
    def describe(self):
        child = self.child()
        if child.__class__.__name__ != "EventItem":
            return str(child)
        else:
            return "no child"

    def __str__(self):
        return str(self.describe)
