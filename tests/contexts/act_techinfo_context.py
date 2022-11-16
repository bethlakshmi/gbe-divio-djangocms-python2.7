from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    EventContainerFactory,
    EventLabelFactory,
    LocationFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
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
                 act_role="Regular Act",
                 set_waitlist=False):
        if conference:
            self.show = show or ShowFactory(e_conference=conference)
        else:
            self.show = show or ShowFactory()
        self.conference = conference or self.show.e_conference
        self.performer = performer or PersonaFactory()
        self.act = act or ActFactory(performer=self.performer,
                                     b_conference=self.conference,
                                     accepted=3,
                                     submitted=True)
        role = "Performer"
        if set_waitlist:
            self.act.accepted = 2
            self.act.save()
            act_role = "Waitlisted"
            role = "Waitlisted"
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
        self.booking = ResourceAllocationFactory(
            event=self.sched_event,
            resource=WorkerFactory(
                _item=self.act.performer,
                role=role))
        self.order = OrderingFactory(
            allocation=self.booking,
            class_id=self.act.pk,
            class_name="Act",
            role=act_role)
        if schedule_rehearsal:
            self.rehearsal = self._schedule_rehearsal(
                self.sched_event,
                self.act)

    def _schedule_rehearsal(self, s_event, act=None):
        rehearsal = GenericEventFactory(type="Rehearsal Slot",
                                        e_conference=self.conference)
        rehearsal_event = SchedEventFactory(
            eventitem=rehearsal.eventitem_ptr,
            max_commitments=10,
            starttime=self.sched_event.starttime)
        event_container = EventContainerFactory(
            child_event=rehearsal_event,
            parent_event=s_event)
        EventLabelFactory(event=rehearsal_event,
                          text=self.conference.conference_slug)
        if act:
            booking = ResourceAllocationFactory(
                event=rehearsal_event,
                resource=WorkerFactory(
                    _item=act.performer,
                    role="Performer"))
            OrderingFactory(
                allocation=booking,
                class_id=act.pk,
                class_name="Act")

        return rehearsal_event

    def order_act(self, act, order):
        alloc = self.sched_event.resources_allocated.filter(
            ordering__class_id=act.pk,
            event=self.sched_event).first()
        ordering, created = Ordering.objects.get_or_create(allocation=alloc)
        ordering.order = order
        ordering.save()

    def make_priv_role(self, role="Stage Manager"):
        profile = ProfileFactory()
        ResourceAllocationFactory(
            event=self.sched_event,
            resource=WorkerFactory(role=role, _item=profile))
        return profile
