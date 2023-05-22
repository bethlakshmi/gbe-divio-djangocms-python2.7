from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    ConferenceFactory,
    ProfileFactory,
    RoomFactory,
    SocialLinkFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    LocationFactory,
    OrderingFactory,
    PeopleAllocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from scheduler.models import Ordering
from tests.functions.scheduler_functions import (
    get_or_create_bio,
    get_or_create_profile,
)
from gbe.models import SocialLink


class ActTechInfoContext():
    def __init__(self,
                 performer=None,
                 act=None,
                 sched_event=None,
                 conference=None,
                 room_name=None,
                 schedule_rehearsal=False,
                 act_role="Regular Act",
                 set_waitlist=False):
        self.conference = conference or ConferenceFactory()
        self.performer = performer or BioFactory()
        self.people = get_or_create_bio(self.performer)
        self.act = act or ActFactory(bio=self.performer,
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
                event_style="Show")
            EventLabelFactory(event=self.sched_event,
                              text=self.conference.conference_slug)
            EventLabelFactory(event=self.sched_event,
                              text="General")
        room_name = room_name or "Dining Room"
        self.room = RoomFactory(name=room_name)
        self.room.conferences.add(self.conference)
        if not sched_event:
            ResourceAllocationFactory(
                event=self.sched_event,
                resource=LocationFactory(_item=self.room.locationitem_ptr))
        # schedule the act into the show
        self.booking = PeopleAllocationFactory(
            event=self.sched_event,
            people=self.people,
            role=role)
        self.order = OrderingFactory(
            people_allocated=self.booking,
            class_id=self.act.pk,
            class_name="Act",
            role=act_role)
        if schedule_rehearsal:
            self.rehearsal = self._schedule_rehearsal(
                self.sched_event,
                self.act)

    def _schedule_rehearsal(self, s_event, act=None):
        rehearsal_event = SchedEventFactory(
            event_style="Rehearsal Slot",
            max_commitments=10,
            starttime=self.sched_event.starttime,
            parent=s_event)
        EventLabelFactory(event=rehearsal_event,
                          text=self.conference.conference_slug)
        if act:
            people = get_or_create_bio(act.bio)
            booking = PeopleAllocationFactory(
                event=rehearsal_event,
                people=people,
                role="Performer")
            OrderingFactory(
                people_allocated=booking,
                class_id=act.pk,
                class_name="Act")
        return rehearsal_event

    def order_act(self, act, order):
        alloc = self.sched_event.peopleallocation_set.filter(
            ordering__class_id=act.pk,
            event=self.sched_event).first()
        ordering, created = Ordering.objects.get_or_create(
            people_allocated=alloc)
        ordering.order = order
        ordering.save()

    def make_priv_role(self, role="Stage Manager"):
        profile = ProfileFactory()
        people = get_or_create_profile(profile)
        PeopleAllocationFactory(
            event=self.sched_event,
            role=role,
            people=people)
        return profile

    def set_social_media(self, social_network="Website"):
        username = None
        link = None
        if social_network in SocialLink.link_template:
            username = "performer_%d" % self.performer.pk
        else:
            link = "www.madethisup%d.com" % self.performer.pk

        return SocialLinkFactory(bio=self.performer,
                                 social_network=social_network,
                                 username=username,
                                 link=link)
