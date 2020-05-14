from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    GenericEventFactory,
    ProfilePreferencesFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
    VolunteerFactory,
    VolunteerInterestFactory
)
from tests.factories.scheduler_factories import (
    EventContainerFactory,
    EventLabelFactory,
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from gbe.models import ConferenceDay
from datetime import (
    date,
    datetime,
    time,
)


class VolunteerContext():
    def __init__(self,
                 profile=None,
                 bid=None,
                 event=None,
                 opportunity=None,
                 role=None,
                 conference=None):
        if not event:
            self.conference = conference or ConferenceFactory()
        else:
            self.conference = event.e_conference
        if ConferenceDay.objects.filter(conference=self.conference).exists():
            self.conf_day = ConferenceDay.objects.filter(
                conference=self.conference).first()
        else:
            self.conf_day = ConferenceDayFactory(conference=self.conference)
        self.profile = profile or ProfileFactory()
        if not hasattr(self.profile, 'preferences'):
            ProfilePreferencesFactory(profile=self.profile)

        if bid is False:
            self.bid = None
        elif bid:
            self.bid = bid
            self.profile = self.bid.profile
        else:
            self.bid = VolunteerFactory(
                b_conference=self.conference,
                profile=self.profile)
        self.interest = VolunteerInterestFactory(
            volunteer=self.bid)
        self.event = event or ShowFactory(
            e_conference=self.conference)
        self.role = role or "Volunteer"
        self.room = RoomFactory()
        self.room.conferences.add(self.conference)

        self.sched_event = SchedEventFactory(
            eventitem=self.event.eventitem_ptr,
            starttime=datetime.combine(self.conf_day.day,
                                       time(12, 0, 0)))
        ResourceAllocationFactory(
            event=self.sched_event,
            resource=LocationFactory(_item=self.room))
        EventLabelFactory(event=self.sched_event,
                          text="General")
        EventLabelFactory(event=self.sched_event,
                          text=self.conference.conference_slug)
        self.worker = WorkerFactory(_item=self.profile.workeritem,
                                    role=self.role)
        self.opportunity, self.opp_event = self.add_opportunity(opportunity)
        self.allocation = ResourceAllocationFactory(resource=self.worker,
                                                    event=self.opp_event)

    def set_staff_lead(self, staff_lead=None):
        staff_lead = staff_lead or ProfileFactory()
        ResourceAllocationFactory(event=self.sched_event,
                                  resource=WorkerFactory(
                                    _item=staff_lead,
                                    role="Staff Lead"))
        return staff_lead

    def add_opportunity(self, opportunity=None, start_time=None):
        opportunity = opportunity or GenericEventFactory(
            e_conference=self.conference,
            type='Volunteer',
            volunteer_type=self.interest.interest)
        start_time = start_time or datetime.combine(
            self.conf_day.day,
            time(12, 0, 0))

        opp_event = SchedEventFactory(
            eventitem=opportunity.eventitem_ptr,
            starttime=start_time,
            max_volunteer=2)
        ResourceAllocationFactory(
            event=opp_event,
            resource=LocationFactory(_item=self.room))
        EventContainerFactory(parent_event=self.sched_event,
                              child_event=opp_event)
        EventLabelFactory(event=opp_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=opp_event,
                          text="Volunteer")
        return opportunity, opp_event
