from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    LocationFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
import pytz
from tests.functions.scheduler_functions import noon
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
        self.performer = performer or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        if not self.conference.conferenceday_set.exists():
            day = ConferenceDayFactory(conference=self.conference)
            if starttime:
                day.day = starttime.date()
                day.save()
        self.days = self.conference.conferenceday_set.all()
        act = act or ActFactory(b_conference=self.conference,
                                performer=self.performer,
                                accepted=3,
                                submitted=True)
        self.acts = [act]
        self.show = ShowFactory(e_conference=self.conference)
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
            sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr,
                                            starttime=starttime,
                                            slug="Show%d" % self.show.pk)
        else:
            sched_event = SchedEventFactory(
                eventitem=self.show.eventitem_ptr,
                starttime=noon(self.days[0]))
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
        ResourceAllocationFactory(event=self.sched_event,
                                  resource=WorkerFactory(
                                    _item=producer,
                                    role="Producer"))
        return producer

    def book_act(self, act=None, act_role='Regular Act'):
        act = act or ActFactory(b_conference=self.conference,
                                accepted=3,
                                submitted=True)
        role = "Performer"
        booking = ResourceAllocationFactory(
            event=self.sched_event,
            resource=WorkerFactory(_item=act.performer, role=role))
        order = OrderingFactory(
            allocation=booking,
            class_id=act.pk,
            class_name="Act",
            role=act_role)
        return (act, booking)

    def set_interest(self, interested_profile=None):
        interested_profile = interested_profile or ProfileFactory()
        ResourceAllocationFactory(event=self.sched_event,
                                  resource=WorkerFactory(
                                    _item=interested_profile,
                                    role="Interested"))
        return interested_profile

    def make_rehearsal(self, room=True):
        rehearsal = GenericEventFactory(
            e_conference=self.conference,
            type='Rehearsal Slot')
        start_time = datetime.combine(
            self.days[0].day,
            (self.sched_event.start_time - timedelta(hours=4)).time())

        slot = SchedEventFactory(
            eventitem=rehearsal.eventitem_ptr,
            starttime=start_time,
            max_commitments=10,
            parent=self.sched_event)
        if room:
            ResourceAllocationFactory(
                event=slot,
                resource=LocationFactory(_item=self.room))
        EventLabelFactory(event=slot,
                          text=self.conference.conference_slug)
        return rehearsal, slot
