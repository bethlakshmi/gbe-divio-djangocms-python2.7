from tests.factories.gbe_factories import (
    GenericEventFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    ProfileFactory,
    RoomFactory,
    StaffAreaFactory,
)
from tests.factories.scheduler_factories import (
    EventContainerFactory,
    EventLabelFactory,
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from tests.functions.scheduler_functions import noon


class StaffAreaContext:
    '''
    Sets up a GenericEvent as a StaffArea in a pattern similar to what we
    create in practice - with some number of volunteer shifts and assigned
    volunteers in the shifts
    '''
    def __init__(self,
                 area=None,
                 staff_lead=None,
                 conference=None,
                 starttime=None):
        self.staff_lead = staff_lead or ProfileFactory()
        self.conference = conference or ConferenceFactory()
        self.area = area or StaffAreaFactory(conference=self.conference,
                                             staff_lead=self.staff_lead)

    def add_volunteer_opp(self):
        if not self.conference.conferenceday_set.exists():
            self.conf_day = ConferenceDayFactory(
                conference=self.conference)
        else:
            self.conf_day = self.conference.conferenceday_set.first()
        vol_event = GenericEventFactory(e_conference=self.conference,
                                        type="Volunteer")
        volunteer_sched_event = SchedEventFactory(
            eventitem=vol_event,
            max_volunteer=self.area.default_volunteers,
            starttime=noon(self.conf_day))
        room = self.get_room()

        ResourceAllocationFactory(
            event=volunteer_sched_event,
            resource=LocationFactory(_item=room))
        EventLabelFactory(event=volunteer_sched_event,
                          text=self.area.slug)
        EventLabelFactory(event=volunteer_sched_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=volunteer_sched_event,
                          text="Volunteer")
        return volunteer_sched_event

    def book_volunteer(self,
                       volunteer_sched_event=None,
                       volunteer=None,
                       role="Volunteer"):
        if not volunteer_sched_event:
            volunteer_sched_event = self.add_volunteer_opp()
        if not volunteer:
            volunteer = ProfileFactory()
        booking = ResourceAllocationFactory(
            event=volunteer_sched_event,
            resource=WorkerFactory(_item=volunteer, role=role))
        return (volunteer, booking)

    def get_room(self):
        room = RoomFactory()
        room.conferences.add(self.conference)
        return room
