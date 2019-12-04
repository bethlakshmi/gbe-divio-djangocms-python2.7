from random import randint
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
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

from gbe.models import Class
from datetime import timedelta
from tests.functions.scheduler_functions import noon


def unique_string(base_string):
    return base_string % str(randint(0, 10000))


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
                                       e_conference=self.conference,
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
            sched_event = SchedEventFactory(eventitem=self.bid.eventitem_ptr,
                                            starttime=starttime)
        elif self.sched_event:
            one_day = timedelta(1)
            sched_event = SchedEventFactory(
                eventitem=self.bid.eventitem_ptr,
                starttime=self.sched_event.starttime+one_day)
        else:
            sched_event = SchedEventFactory(
                eventitem=self.bid.eventitem_ptr,
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
