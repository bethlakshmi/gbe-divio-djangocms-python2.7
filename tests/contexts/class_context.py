from random import randint
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
    SocialLinkFactory,
)
from tests.factories.scheduler_factories import (
    EventEvalGradeFactory,
    EventEvalQuestionFactory,
    EventLabelFactory,
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)

from gbe.models import (
    Class,
    SocialLink,
)
from datetime import timedelta
from tests.functions.scheduler_functions import noon
from tests.factories.ticketing_factories import TicketItemFactory


class ClassContext:
    def __init__(self,
                 bid=None,
                 teacher=None,
                 conference=None,
                 room=None,
                 starttime=None):
        self.teacher = teacher or PersonaFactory()
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
                                       teacher=self.teacher,
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
        ResourceAllocationFactory(
            event=sched_event,
            resource=WorkerFactory(_item=teacher.workeritem_ptr,
                                   role='Teacher'))
        EventLabelFactory(event=sched_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=sched_event,
                          text="Conference")
        return sched_event

    def set_interest(self, interested_profile=None):
        interested_profile = interested_profile or ProfileFactory()
        ResourceAllocationFactory(event=self.sched_event,
                                  resource=WorkerFactory(
                                    _item=interested_profile,
                                    role="Interested"))
        return interested_profile

    def setup_eval(self):
        return EventEvalQuestionFactory()

    def set_eval_answerer(self, eval_profile=None):
        eval_profile = eval_profile or ProfileFactory()
        answer = EventEvalGradeFactory(profile=eval_profile,
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

    def set_social_media(self, social_network="Website"):
        username = None
        link = None
        if social_network in SocialLink.link_template:
            username = "teacher_%d" % self.teacher.pk
        else:
            link = "www.madethisup%d.com" % self.teacher.pk

        return SocialLinkFactory(performer=self.teacher,
                                 social_network=social_network,
                                 username=username,
                                 link=link)
