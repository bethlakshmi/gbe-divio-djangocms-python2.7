from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    ProfilePreferencesFactory,
    ProfileFactory,
    RoomFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    LocationFactory,
    PeopleAllocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from gbe.models import ConferenceDay
from datetime import (
    date,
    datetime,
    time,
)
from tests.functions.scheduler_functions import get_or_create_profile


class VolunteerContext():
    def __init__(self,
                 profile=None,
                 sched_event=None,
                 opportunity=None,
                 role=None,
                 conference=None,
                 event_style="Show"):
        self.conference = conference or ConferenceFactory()

        if ConferenceDay.objects.filter(conference=self.conference).exists():
            self.conf_day = ConferenceDay.objects.filter(
                conference=self.conference).first()
        else:
            self.conf_day = ConferenceDayFactory(conference=self.conference)
        self.profile = profile or ProfileFactory()
        self.people = get_or_create_profile(self.profile)
        if not hasattr(self.profile, 'preferences'):
            ProfilePreferencesFactory(profile=self.profile)

        self.role = role or "Volunteer"
        self.room = RoomFactory()
        self.room.conferences.add(self.conference)

        if not sched_event:
            self.sched_event = SchedEventFactory(
                event_style=event_style,
                starttime=datetime.combine(self.conf_day.day,
                                           time(12, 0, 0)),
                slug="Show%d" % self.profile.pk)
            ResourceAllocationFactory(
                event=self.sched_event,
                resource=LocationFactory(_item=self.room))
            EventLabelFactory(event=self.sched_event,
                              text="General")
            EventLabelFactory(event=self.sched_event,
                              text=self.conference.conference_slug)
        else:
            self.sched_event = sched_event

        self.opp_event = self.add_opportunity(opportunity)
        self.allocation = PeopleAllocationFactory(people=self.people,
                                                  role=self.role,
                                                  event=self.opp_event)

    def set_staff_lead(self, staff_lead=None, role=None):
        staff_lead = staff_lead or ProfileFactory()
        staff_lead_people = get_or_create_profile(staff_lead)
        role = role or "Staff Lead"
        PeopleAllocationFactory(event=self.sched_event,
                                people=staff_lead_people,
                                role=role)
        return staff_lead

    def add_opportunity(self, start_time=None):
        start_time = start_time or datetime.combine(
            self.conf_day.day,
            time(12, 0, 0))

        opp_event = SchedEventFactory(
            event_style='Volunteer',
            starttime=start_time,
            max_volunteer=2,
            parent=self.sched_event)
        ResourceAllocationFactory(
            event=opp_event,
            resource=LocationFactory(_item=self.room))

        EventLabelFactory(event=opp_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=opp_event,
                          text="Volunteer")
        return opp_event
