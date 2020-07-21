from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator
from scheduler.models import (
    ActItem,
    ActResource,
    Location,
    LocationItem,
    Resource,
    ResourceItem,
    Schedulable,
)
from scheduler.data_transfer import (
    Person,
    BookingResponse,
    Warning,
    Error,
)
from datetime import datetime, timedelta
from model_utils.managers import InheritanceManager
from gbetext import *
from settings import GBE_DATETIME_FORMAT
from django.utils.formats import date_format
from django.core.exceptions import MultipleObjectsReturned
import pytz


class WorkerItem(ResourceItem):
    '''
    Payload object for a person as resource (staff/volunteer/teacher)
    '''
    objects = InheritanceManager()

    @property
    def as_subtype(self):
        '''
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
                eventitem__event__e_conference=conference)
        return events


class Worker(Resource):
    '''
    objects = InheritanceManager()
    An allocatable person
    '''
    _item = models.ForeignKey(WorkerItem, on_delete=models.CASCADE)
    role = models.CharField(max_length=50,
                            choices=role_options,
                            blank=True)

    @property
    def workeritem(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self._item.resourceitem_id)

    @property
    def type(self):
        return self.role

    def __str__(self):
        return self.item.describe


class EventItem (models.Model):
    '''
    The payload for an event (ie, a class, act, show, or generic event)
    The EventItem must not impose any DB usage on its implementing model
    classes.
    '''
    objects = InheritanceManager()
    eventitem_id = models.AutoField(primary_key=True)
    visible = models.BooleanField(default=True)

    def child(self):
        return EventItem.objects.get_subclass(eventitem_id=self.eventitem_id)

    def get_conference(self):
        return self.child().e_conference

    # DEPRECATE - when scheduling refactored
    def roles(self, roles=['Teacher',
                           'Panelist',
                           'Moderator',
                           'Staff Lead']):
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


class Event(Schedulable):
    '''
    An Event is a schedulable item with a conference model item as its payload.
    '''
    objects = InheritanceManager()
    eventitem = models.ForeignKey(EventItem,
                                  on_delete=models.CASCADE,
                                  related_name="scheduler_events")
    starttime = models.DateTimeField(blank=True)
    max_volunteer = models.PositiveIntegerField(default=0)
    approval_needed = models.BooleanField(default=False)

    def has_act_opening(self):
        '''
        returns True if the count of acts allocated to this event is less than
        max_volunteer
        '''
        allocs = ResourceAllocation.objects.filter(event=self)
        acts_booked = len([a for a in allocs
                           if isinstance(a.resource.as_subtype, ActResource)])
        return self.max_volunteer - acts_booked > 0

    @property
    def foreign_event_id(self):
        return self.eventitem.eventitem_id

    # New - fits scheduling API refactor
    def set_locations(self, locations):
        '''
        Takes a LIST of locations, removes all existing location settings
        and replaces them with the given list.  Locations are expected to be
        location items
        '''
        for assignment in ResourceAllocation.objects.filter(event=self):
            if assignment.resource.as_subtype.__class__.__name__ == "Location":
                assignment.delete()
        for location in locations:
            if location is not None:
                try:
                    loc = Location.objects.select_subclasses().get(
                        _item=location)
                except:
                    loc = Location(_item=location)
                    loc.save()
                ra = ResourceAllocation(resource=loc, event=self)
                ra.save()

    # New - from refactoring
    @property
    def people(self):
        people = []
        for booking in ResourceAllocation.objects.filter(event=self):
            if booking.resource.as_subtype.__class__.__name__ == "Worker":
                person = Person(booking=booking)
                if hasattr(booking, 'label'):
                    person.label = booking.label.text
                people += [person]
        return people

    # New - from refactoring
    def allocate_person(self, person):
        '''
        allocated worker for the new model - right now, focused on create
        uses the Person from the data_transfer objects.
        '''
        from scheduler.idd import get_schedule

        warnings = []
        time_format = GBE_DATETIME_FORMAT

        worker = None
        if person.public_id:
            item = WorkerItem.objects.get(pk=person.public_id)
            worker = Worker(_item=item, role=person.role)

        else:
            worker = Worker(_item=person.user.profile, role=person.role)
        worker.save()

        for conflict in get_schedule(
                    user=worker.workeritem.user_object,
                    start_time=self.start_time,
                    end_time=self.end_time).schedule_items:
            warnings += [Warning(code="SCHEDULE_CONFLICT",
                                 user=person.user,
                                 occurrence=conflict.event)]
        if person.booking_id:
            allocation = ResourceAllocation.objects.get(
                id=person.booking_id)
            allocation.resource = worker
        else:
            allocation = ResourceAllocation(event=self,
                                            resource=worker)
        allocation.save()
        if self.extra_volunteers() > 0:
            warnings += [Warning(
                code="OCCURRENCE_OVERBOOKED",
                details="Over booked by %s volunteers" % (
                    self.extra_volunteers()))]
        if person.label:
            allocation.set_label(person.label)
        return BookingResponse(warnings=warnings,
                               booking_id=allocation.pk,
                               occurrence=self)

    # New - from refactoring
    def allocate_act(self, act):
        '''
        allocated worker for the new model - right now, focused on create
        uses the BookableAct from the data_transfer objects.
        '''
        warnings = []
        time_format = GBE_DATETIME_FORMAT

        worker = None
        item = ActItem.objects.get(pk=act.act_id)
        resource = ActResource(_item=item)
        if act.role:
            resource.role = act.role
        resource.save()

        if act.booking_id:
            try:
                allocation = ResourceAllocation.objects.get(
                    id=act.booking_id)
                allocation.resource = resource
                allocation.event = self
            except ResourceAllocation.DoesNotExist:
                return BookingResponse(
                    errors=[Error(
                        code="BOOKING_NOT_FOUND",
                        details="Booking id %s not found" % act.booking_id), ],
                    booking_id=act.booking_id)
        else:
            allocation = ResourceAllocation(event=self,
                                            resource=resource)
        allocation.save()

        num_acts = ActResource.objects.filter(
                allocations__event=self).count()
        if num_acts > self.max_volunteer:
            warnings += [Warning(
                code="OCCURRENCE_OVERBOOKED",
                details="Over booked by %s acts" % (
                    num_acts - self.max_volunteer))]
        if act.order:
            ordering = Ordering.objects.get_or_create(allocation=allocation)
            ordering[0].order = act.order
            ordering[0].save()
        return BookingResponse(warnings=warnings,
                               booking_id=allocation.pk,
                               occurrence=self)

    @property
    def volunteer_count(self):
        allocations = ResourceAllocation.objects.filter(event=self)
        volunteers = allocations.filter(
            resource__worker__role='Volunteer').count()
        if volunteers > 0:
            return "%d volunteers" % volunteers
        else:
            acts = ActResource.objects.filter(
                allocations__in=allocations).count()
            if acts > 0:
                return "%d acts" % acts
        return 0

    def get_acts(self):
        '''
        Returns a list of acts allocated to this event,
        filtered by acceptance status if specified
        '''
        allocations = ResourceAllocation.objects.filter(event=self)
        act_resources = [ar.resource_ptr for ar in ActResource.objects.all()]
        acts = [allocation.resource.item.act for allocation in allocations
                if allocation.resource in act_resources]
        return acts

    @property
    def event_type_name(self):
        '''
        Get event type name. Uses a database call
        '''
        return self.event_type.__name__

    @property
    def event_type(self):
        '''
        Get event's underlying type (ie, conference model)
        '''
        return type(self.as_subtype)

    @property
    def as_subtype(self):
        '''
        Get the representation of this Event as its underlying conference type
        '''
        return EventItem.objects.get_subclass(eventitem_id=self.eventitem_id)

    @property
    def duration(self):
        return self.eventitem.child().sched_duration

    # get castings as in what acts have been booked for this event
    @property
    def casting_list(self):
        return ActResource.objects.filter(
            allocations__event=self,
            _item__act__accepted=3).order_by('_item__act__performer__name')

    def __str__(self):
        return self.eventitem.describe

    @property
    def location(self):
        l = Location.objects.filter(allocations__event=self)
        if len(l) > 0:
            return l[0]._item
        else:
            return None  # or what??

    def extra_volunteers(self):
        '''
        The difference between the max suggested # of volunteers
        and the actual number
        > 0 if there are too many volunteers for the max. The number
        will be the # of people over booked
        (if there are 3 spaces, and 4 volunteers, the value returned is 1)
        = 0 if it is at capacity
        < 0 if it is fewer than the max, the abosolute value is the
        amount of space remaining (if there are 4 spaces, and 3 volunteers,
        the value will be -1)
        '''
        count = Worker.objects.filter(allocations__event=self,
                                      role='Volunteer').count()
        return count - self.max_volunteer

    # New with Scheduler API
    def add_label(self, label):
        label = EventLabel(text=label, event=self)
        label.save()
        return label

    # New with Scheduler API
    @property
    def labels(self):
        return self.eventlabel_set.values_list('text', flat=True)


class ResourceAllocation(Schedulable):
    '''
    Joins a particular Resource to a particular Event
    ResourceAllocations get their scheduling data from their Event.
    '''
    objects = InheritanceManager()
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE,
                              related_name="resources_allocated")
    resource = models.ForeignKey(Resource,
                                 on_delete=models.CASCADE,
                                 related_name="allocations")

    def get_label(self):
        try:
            return self.label
        except Label.DoesNotExist:
            l = Label(allocation=self, text="")
            l.save()
            return l

    def set_label(self, text):
        l = self.get_label()
        l.text = text
        l.save()


class Ordering(models.Model):
    '''
    A decorator for Allocations to allow representation of orderings
    Attaches to an Allocation. No effort is made to ensure uniqueness or
    completeness of an ordering, this is handled later in the business
    logic.
    Orderings are assumed to sort from low to high. Negative ordering
    indices are allowed.
    '''
    order = models.IntegerField(default=0)
    allocation = models.OneToOneField(ResourceAllocation,
                                      on_delete=models.CASCADE)


class Label (models.Model):
    '''
    A decorator allowing free-entry "tags" on allocations
    '''
    text = models.TextField(default='')
    allocation = models.OneToOneField(ResourceAllocation,
                                      on_delete=models.CASCADE)


class EventLabel (models.Model):
    '''
    A decorator allowing free-entry "tags" on allocations
    '''
    text = models.CharField(default='', max_length=200)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        app_label = "scheduler"
        unique_together = (('text', 'event'), )


class EventContainer (models.Model):
    '''
    Another decorator. Links one Event to another. Used to link
    a volunteer shift (Generic Event) to a Show (or other conf event)
    '''
    parent_event = models.ForeignKey(Event,
                                     on_delete=models.CASCADE,
                                     related_name='contained_events')
    child_event = models.OneToOneField(Event,
                                       on_delete=models.CASCADE,
                                       related_name='container_event')
