from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    EventContainerFactory,
    EventLabelFactory,
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from scheduler.models import Ordering


class ActTechInfoContext():
    def __init__(self,
                 performer=None,
                 act=None,
                 show=None,
                 sched_event=None,
                 conference=None,
                 room_name=None,
                 schedule_rehearsal=False,
                 act_role="",
                 set_waitlist=False):
        self.show = show or ShowFactory()
        self.conference = conference or self.show.e_conference
        self.performer = performer or PersonaFactory()
        self.act = act or ActFactory(performer=self.performer,
                                     b_conference=self.conference,
                                     accepted=3,
                                     submitted=True)
        if set_waitlist:
            self.act.accepted = 2
            self.act.save()
            act_role = "Waitlisted"
        self.tech = self.act.tech

        # schedule the show
        if sched_event:
            self.sched_event = sched_event
        else:
            self.sched_event = SchedEventFactory(
                eventitem=self.show.eventitem_ptr)
            EventLabelFactory(event=self.sched_event,
                              text=self.conference.conference_slug)
        room_name = room_name or "Dining Room"
        self.room = RoomFactory(name=room_name)
        self.room.conferences.add(self.conference)
        if not sched_event:
            ResourceAllocationFactory(
                event=self.sched_event,
                resource=LocationFactory(_item=self.room.locationitem_ptr))
        # schedule the act into the show
        ResourceAllocationFactory(
            event=self.sched_event,
            resource=ActResourceFactory(
                _item=self.act.actitem_ptr,
                role=act_role))
        if schedule_rehearsal:
            self.rehearsal = self._schedule_rehearsal(
                self.sched_event,
                self.act)

    def _schedule_rehearsal(self, s_event, act=None):
        rehearsal = GenericEventFactory(type="Rehearsal Slot",
                                        e_conference=self.conference)
        rehearsal_event = SchedEventFactory(
            eventitem=rehearsal.eventitem_ptr,
            max_volunteer=10,
            starttime=self.sched_event.starttime)
        event_container = EventContainerFactory(
            child_event=rehearsal_event,
            parent_event=s_event)
        EventLabelFactory(event=rehearsal_event,
                          text=self.conference.conference_slug)
        if act:
            ResourceAllocationFactory(
                resource=ActResourceFactory(_item=act.actitem_ptr),
                event=rehearsal_event)
        return rehearsal_event

    def order_act(self, act, order):
        alloc = self.sched_event.resources_allocated.filter(
            resource__actresource___item=act).first()
        ordering, created = Ordering.objects.get_or_create(allocation=alloc)
        ordering.order = order
        ordering.save()
