from django.db.models import (
    BooleanField,
    CASCADE,
    DateTimeField,
    ForeignKey,
    PositiveIntegerField,
)
from scheduler.models import (
    ActItem,
    EventItem,
    Location,
    LocationItem,
    Resource,
    ResourceItem,
    Schedulable,
    WorkerItem,
    Worker,
)
from scheduler.data_transfer import (
    Person,
    BookingResponse,
    Warning,
    Error,
)
from model_utils.managers import InheritanceManager
from settings import GBE_DATETIME_FORMAT


class Event(Schedulable):
    '''
    An Event is a schedulable item with a conference model item as its payload.
    '''
    objects = InheritanceManager()
    eventitem = ForeignKey(EventItem,
                           on_delete=CASCADE,
                           related_name="scheduler_events")
    starttime = DateTimeField(blank=True)
    max_volunteer = PositiveIntegerField(default=0)
    approval_needed = BooleanField(default=False)

    def has_act_opening(self):
        '''
        REFACTOR
        '''
        pass

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
        from scheduler.models import ResourceAllocation
        for assignment in self.resources_allocated.all():
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
        for booking in self.resources_allocated.all():
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
        from scheduler.models import (
            Ordering,
            ResourceAllocation,
        )

        warnings = []
        time_format = GBE_DATETIME_FORMAT

        worker = None
        if person.public_id:
            item = WorkerItem.objects.get(pk=person.public_id)
            worker = Worker(_item=item, role=person.role)
        else:
            worker = Worker(_item=person.user.profile, role=person.role)
        worker.save()

        if person.user:
            users = [person.user]
        elif person.users:
            users = person.users
        else:
            users = [worker.workeritem.user_object]

        for user in users:
            for conflict in get_schedule(
                        user=user,
                        start_time=self.start_time,
                        end_time=self.end_time).schedule_items:
                if person.booking_id and (
                        person.booking_id != conflict.booking_id):
                    warnings += [Warning(code="SCHEDULE_CONFLICT",
                                         user=user,
                                         occurrence=conflict.event)]
        if person.booking_id:
            allocation = ResourceAllocation.objects.get(
                id=person.booking_id)
            allocation.resource = worker
        else:
            allocation = ResourceAllocation(event=self,
                                            resource=worker)
        allocation.save()
        if person.commitment:
            ordering, created = Ordering.objects.get_or_create(
                allocation=allocation)
            ordering.role = person.commitment.role
            ordering.class_name = person.commitment.class_name
            ordering.class_id = person.commitment.class_id
            ordering.save()
        if self.extra_volunteers() > 0:
            warnings += [Warning(
                code="OCCURRENCE_OVERBOOKED",
                details="Over booked by %s volunteers" % (
                    self.extra_volunteers()))]
        if person.label:
            # refactor
            from scheduler.models import Label
            l, created = Label.objects.get_or_create(allocation=allocation)
            l.text = person.label
            l.save()
        return BookingResponse(warnings=warnings,
                               booking_id=allocation.pk,
                               occurrence=self)

    @property
    def volunteer_count(self):
        allocations = self.resources_allocated.all()
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
        allocations = self.resources_allocated.all()
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
    @property
    def labels(self):
        return self.eventlabel_set.values_list('text', flat=True)
