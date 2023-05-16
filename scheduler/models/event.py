from django.db.models import (
    BooleanField,
    CharField,
    CASCADE,
    DateTimeField,
    DurationField,
    ForeignKey,
    ManyToManyField,
    PositiveIntegerField,
    SlugField,
    TextField,
)
from scheduler.models import (
    Location,
    LocationItem,
    People,
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
from settings import GBE_DATETIME_FORMAT


class Event(Schedulable):
    '''
    An Event is a schedulable item with a conference model item as its payload.
    '''
    starttime = DateTimeField(blank=True)
    max_volunteer = PositiveIntegerField(default=0)
    approval_needed = BooleanField(default=False)
    max_commitments = PositiveIntegerField(default=0)
    parent = ForeignKey(
        "self",
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="children")
    slug = SlugField(null=True)

    # from gbe.event
    title = CharField(max_length=128)
    description = TextField(blank=True, null=True)
    blurb = TextField(blank=True)
    length = DurationField()

    event_style = CharField(max_length=128, blank=False)
    connected_id = PositiveIntegerField(blank=True, null=True)
    connected_class = CharField(max_length=128, blank=True)

    def has_commitment_space(self, commitment_class_name):
        from scheduler.models import Ordering
        return (Ordering.objects.filter(
            allocation__event=self,
            class_name=commitment_class_name).count() < self.max_commitments)

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
        for booking in self.people_allocations.all():
            person = Person(booking=booking)
            if hasattr(booking, 'label'):
                person.label = booking.label
            people += [person]
        return people

    # New - from refactoring
    def allocate_person(self, person):
        '''
        allocated people for the new model - right now, focused on create
        uses the Person from the data_transfer objects.
        '''
        from scheduler.idd import get_schedule
        from scheduler.models import (
            Ordering,
            PeopleAllocation,
        )

        warnings = []
        time_format = GBE_DATETIME_FORMAT

        people = None
        if person.public_id:
            if People.objects.filter(
                    class_name=person.public_class,
                    class_id=person.public_id).exists():
                people = People.objects.get(class_name=person.public_class,
                                            class_id=person.public_id)
                people.users.all().delete()
            else:
                people = People(class_name=person.public_class,
                                class_id=person.public_id)
                people.save()

        else:
            raise Exception("Person public id required")

        for user in person.users:
            people.users.add(user)
            for conflict in get_schedule(
                        user=user,
                        start_time=self.start_time,
                        end_time=self.end_time).schedule_items:
                if not person.booking_id or (
                        person.booking_id != conflict.booking_id):
                    warnings += [Warning(code="SCHEDULE_CONFLICT",
                                         user=user,
                                         occurrence=conflict.event)]
        if person.booking_id:
            allocation = PeopleAllocation.objects.get(
                id=person.booking_id)
            allocation.people = people
            allocation.event = self
            allocation.role = person.role
        else:
            allocation = PeopleAllocation(event=self,
                                          people=people,
                                          role = person.role)
        allocation.save()
        if person.commitment:
            ordering, created = Ordering.objects.get_or_create(
                people_allocated=allocation)
            if person.commitment.role is not None:
                ordering.role = person.commitment.role
            if person.commitment.order:
                ordering.order = person.commitment.order
            ordering.class_name = person.commitment.class_name
            ordering.class_id = person.commitment.class_id
            ordering.save()
        if self.extra_volunteers() > 0:
            warnings += [Warning(
                code="OCCURRENCE_OVERBOOKED",
                details="Over booked by %s volunteers" % (
                    self.extra_volunteers()))]
        if person.label:
            allocation.label = person.label
            allocation.save()
        return BookingResponse(warnings=warnings,
                               booking_id=allocation.pk,
                               occurrence=self)

    def role_count(self, role="Volunteer"):
        return self.people_allocations.filter(role=role).count()

    @property
    def duration(self):
        return self.length

    def __str__(self):
        return self.title

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
        return self.role_count - self.max_volunteer

    # New with Scheduler API
    @property
    def labels(self):
        return self.eventlabel_set.values_list('text', flat=True)

    class Meta:
        app_label = "scheduler"
