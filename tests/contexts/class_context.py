from random import randint
from tests.factories.gbe_factories import (
    BioFactory,
    ClassFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    ProfileFactory,
    RoomFactory,
    SocialLinkFactory,
)
from tests.factories.scheduler_factories import (
    EventEvalGradeFactory,
    EventEvalQuestionFactory,
    EventLabelFactory,
    LocationFactory,
    PeopleAllocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from tests.functions.scheduler_functions import (
    get_or_create_bio,
    get_or_create_profile,
    noon,
)
from gbe.models import (
    Class,
    SocialLink,
)
from datetime import timedelta
from tests.factories.ticketing_factories import (
    TicketItemFactory,
    TicketPackageFactory,
    TicketTypeFactory,
)


class ClassContext:
    def __init__(self,
                 bid=None,
                 teacher=None,
                 conference=None,
                 room=None,
                 starttime=None):
        self.teacher = teacher or BioFactory()
        self.people = get_or_create_bio(self.teacher)

        self.conference = conference or ConferenceFactory()
        if not self.conference.conferenceday_set.exists():
            day = ConferenceDayFactory(conference=self.conference)
            if starttime:
                day.day = starttime.date()
                day.save()

        self.days = self.conference.conferenceday_set.all()
        self.starttime = starttime or noon(self.days[0])
        self.bid = bid or ClassFactory(b_conference=self.conference,
                                       accepted=3,
                                       teacher_bio=self.teacher,
                                       submitted=True)
        self.room = room or RoomFactory()
        self.room.conferences.add(self.conference)
        self.sched_event = None
        self.sched_event = self.schedule_instance(room=self.room,
                                                  starttime=starttime)

    def schedule_instance(self,
                          starttime=None,
                          room=None,
                          teacher=None):
        room = room or self.room
        teacher = teacher or self.teacher
        if starttime:
            sched_event = SchedEventFactory(
                title=self.bid.b_title,
                description=self.bid.b_description,
                event_style=self.bid.type,
                connected_id=self.bid.pk,
                connected_class=self.bid.__class__.__name__,
                starttime=starttime)
        else:
            sched_event = SchedEventFactory(
                title=self.bid.b_title,
                description=self.bid.b_description,
                connected_id=self.bid.pk,
                event_style=self.bid.type,
                connected_class=self.bid.__class__.__name__,
                starttime=noon(self.days[0]))
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        PeopleAllocationFactory(
            event=sched_event,
            role='Teacher',
            people=self.people)
        EventLabelFactory(event=sched_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=sched_event,
                          text="Conference")
        return sched_event

    def set_interest(self, interested_profile=None):
        interested_profile = interested_profile or ProfileFactory()
        interested_people = get_or_create_profile(interested_profile)
        PeopleAllocationFactory(event=self.sched_event,
                                role="Interested",
                                people=interested_people)
        return interested_profile

    def setup_eval(self):
        return EventEvalQuestionFactory()

    def set_eval_answerer(self, eval_profile=None):
        eval_profile = eval_profile or ProfileFactory()
        answer = EventEvalGradeFactory(user=eval_profile.user_object,
                                       event=self.sched_event)
        return eval_profile

    def setup_tickets(self):
        package = TicketItemFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__include_conference=True,
            live=True,
            has_coupon=False)
        this_class = TicketItemFactory(
            ticketing_event__conference=self.conference,
            live=True,
            has_coupon=False)
        this_class.ticketing_event.linked_events.add(self.sched_event)
        return package, this_class

    def setup_ticket_type(self):
        ticket_type = TicketTypeFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__source=3,
            ticketing_event__slug="testslug",
            live=True,
            has_coupon=False,
            conference_only_pass=True)
        return ticket_type

    def setup_package(self):
        package = TicketPackageFactory(
            ticketing_event__conference=self.conference,
            ticketing_event__source=3,
            ticketing_event__slug="testpackageslug",
            whole_shebang=True,
            live=True,
            has_coupon=False)
        return package

    def set_social_media(self, social_network="Website"):
        username = None
        link = None
        if social_network in SocialLink.link_template:
            username = "teacher_%d" % self.teacher.pk
        else:
            link = "www.madethisup%d.com" % self.teacher.pk

        return SocialLinkFactory(bio=self.teacher,
                                 social_network=social_network,
                                 username=username,
                                 link=link)
