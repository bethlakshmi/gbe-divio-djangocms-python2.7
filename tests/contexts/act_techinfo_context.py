from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    CueInfoFactory,
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


class ActTechInfoContext():
    def __init__(self,
                 performer=None,
                 act=None,
                 show=None,
                 sched_event=None,
                 conference=None,
                 room_name=None,
                 cue_count=1,
                 schedule_rehearsal=False,
                 act_role=""):
        self.show = show or ShowFactory()
        self.conference = conference or self.show.e_conference
        self.performer = performer or PersonaFactory()
        self.act = act or ActFactory(performer=self.performer,
                                     b_conference=self.conference,
                                     accepted=3,
                                     submitted=True)
        self.tech = self.act.tech
        self.audio = self.tech.audio
        self.lighting = self.tech.lighting
        self.stage = self.tech.stage
        for i in range(cue_count):
            CueInfoFactory.create(techinfo=self.tech,
                                  cue_sequence=i)
        # schedule the show
        self.sched_event = sched_event or SchedEventFactory(
            eventitem=self.show.eventitem_ptr)
        room_name = room_name or "Dining Room"
        self.room = RoomFactory(name=room_name)
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
