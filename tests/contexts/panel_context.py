from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    PersonaFactory,
    RoomFactory,
)
from tests.factories.scheduler_factories import (
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)


class PanelContext:
    def __init__(self,
                 bid=None,
                 moderator=None,
                 conference=None,
                 room=None,
                 starttime=None):
        self.moderator = moderator or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        self.bid = bid or ClassFactory(b_conference=self.conference,
                                       e_conference=self.conference,
                                       accepted=3)
        self.room = room or RoomFactory()
        self.sched_event = None
        self.sched_event = self.schedule_instance(room=self.room,
                                                  starttime=starttime)
        self.days = [ConferenceDayFactory(conference=self.conference)]

    def schedule_instance(self,
                          starttime=None,
                          room=None,
                          moderator=None):
        room = room or self.room
        moderator = moderator or self.moderator
        if starttime:
            sched_event = SchedEventFactory(eventitem=self.bid.eventitem_ptr,
                                            starttime=starttime)
        elif self.sched_event:
            one_day = timedelta(1)
            sched_event = SchedEventFactory(
                eventitem=self.bid.eventitem_ptr,
                starttime=self.sched_event.starttime+one_day)
        else:
            sched_event = SchedEventFactory(eventitem=self.bid.eventitem_ptr)
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        ResourceAllocationFactory(
            event=sched_event,
            resource=WorkerFactory(_item=moderator.workeritem_ptr,
                                   role='Moderator'))
        return sched_event

    def add_panelist(self,
                     panelist=None):
        panelist = panelist or PersonaFactory()
        ResourceAllocationFactory(
            event=self.sched_event,
            resource=WorkerFactory(_item=panelist.workeritem_ptr,
                                   role='Panelist'))
        return panelist
