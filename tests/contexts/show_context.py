from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    ProfileFactory,
    RoomFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    LocationFactory,
    OrderingFactory,
    PeopleAllocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from tests.factories.ticketing_factories import (
    TicketItemFactory,
    TicketTypeFactory,
    TicketPackageFactory,
)
import pytz
from tests.functions.scheduler_functions import (
    get_or_create_bio,
    get_or_create_profile,
    noon,
)
from datetime import (
    datetime,
    timedelta,
)
from scheduler.models import Ordering


class ShowContext:
    def __init__(self,
                 act=None,
                 performer=None,
                 conference=None,
                 room=None,
                 starttime=None,
                 act_role='Regular Act'):
        self.performer = performer or BioFactory()
        self.conference = conference or ConferenceFactory()
        if not self.conference.conferenceday_set.exists():
            day = ConferenceDayFactory(conference=self.conference)
            if starttime:
                day.day = starttime.date()
                day.save()
        self.days = self.conference.conferenceday_set.all()
        act = act or ActFactory(b_conference=self.conference,
                                bio=self.performer,
                                accepted=3,
                                submitted=True)
        self.acts = [act]
        self.people = get_or_create_bio(self.performer,
                                        act.__class__.__name__,
                                        act.pk)
        self.room = room or RoomFactory()
        self.room.conferences.add(self.conference)
        self.sched_event = None
        self.sched_event = self.schedule_instance(room=self.room,
                                                  starttime=starttime)
        self.book_act(act, act_role)

    def schedule_instance(self,
                          starttime=None,
                          room=None):
        room = room or self.room
        if starttime:
            sched_event = SchedEventFactory(event_style="Show",
                                            starttime=starttime,
                                            slug="Show%d" % self.room.pk)
        else:
            sched_event = SchedEventFactory(
                event_style="Show",
                starttime=noon(self.days[0]),
                slug="Show%d" % self.room.pk)
        EventLabelFactory(event=sched_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=sched_event,
                          text="General")
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        return sched_event

    def set_producer(self, producer=None):
        producer = producer or ProfileFactory()
        prod_people = get_or_create_profile(producer)
        PeopleAllocationFactory(event=self.sched_event,
                                people=prod_people,
                                role="Producer")
        return producer

    def book_act(self, act=None, act_role='Regular Act'):
        act = act or ActFactory(b_conference=self.conference,
                                accepted=3,
                                submitted=True)
        performer = get_or_create_bio(act.bio, act.__class__.__name__, act.pk)
        role = "Performer"
        booking = PeopleAllocationFactory(
            event=self.sched_event,
            people=performer,
            role=role)
        order = OrderingFactory(
            people_allocated=booking,
            role=act_role)
        return (act, booking)

    def set_interest(self, interested_profile=None):
        interested_profile = interested_profile or ProfileFactory()
        people = get_or_create_profile(interested_profile)
        PeopleAllocationFactory(event=self.sched_event,
                                people=people,
                                role="Interested")
        return interested_profile

    def make_rehearsal(self, room=True):
        start_time = datetime.combine(
            self.days[0].day,
            (self.sched_event.start_time - timedelta(hours=4)).time())

        slot = SchedEventFactory(
            event_style='Rehearsal Slot',
            starttime=start_time,
            max_commitments=10,
            parent=self.sched_event)
        if room:
            ResourceAllocationFactory(
                event=slot,
                resource=LocationFactory(_item=self.room))
        EventLabelFactory(event=slot,
                          text=self.conference.conference_slug)
        return slot

    def setup_tickets(self):
        package = TicketItemFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__include_most=True,
            live=True,
            has_coupon=False)
        this_show = TicketItemFactory(
            ticketing_event__conference=self.conference,
            live=True,
            has_coupon=False)
        this_show.ticketing_event.linked_events.add(self.sched_event)
        return package, this_show

    def setup_ticket_type(self):
        this_show = TicketTypeFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__source=3,
            ticketing_event__slug="testslug",
            live=True,
            has_coupon=False)
        this_show.linked_events.add(self.sched_event)
        return this_show

    def setup_package(self):
        package = TicketPackageFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__source=3,
            ticketing_event__slug="testpackageslug",
            whole_shebang=True,
            live=True,
            has_coupon=False)
        return package

    def setup_composite_package(self):
        ticket_type = self.setup_ticket_type()
        package = TicketPackageFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__source=3,
            ticketing_event__slug="testpackageslug",
            whole_shebang=False,
            live=True,
            has_coupon=False)
        package.ticket_types.add(ticket_type)
        return ticket_type, package

