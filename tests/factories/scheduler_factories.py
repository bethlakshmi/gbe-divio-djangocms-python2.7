from factory import (
    SubFactory,
    RelatedFactory,
    Sequence
)
from factory.django import DjangoModelFactory
import scheduler.models as sched
from datetime import datetime
from tests.factories.gbe_factories import (
    GenericEventFactory,
    ProfileFactory,
)


class SchedulableFactory(DjangoModelFactory):
    class Meta:
        model = sched.Schedulable


class ResourceItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.ResourceItem


class ResourceFactory(DjangoModelFactory):
    class Meta:
        model = sched.Resource


class LocationItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.LocationItem


class LocationFactory(DjangoModelFactory):
    _item = SubFactory(LocationItemFactory)

    class Meta:
        model = sched.Location


class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.WorkerItem


class WorkerFactory(DjangoModelFactory):
    _item = SubFactory(WorkerItemFactory)
    role = "Volunteer"

    class Meta:
        model = sched.Worker


class EventItemFactory(DjangoModelFactory):
    visible = True

    class Meta:
        model = sched.EventItem


class SchedEventFactory(DjangoModelFactory):
    eventitem = SubFactory(GenericEventFactory)
    starttime = datetime(2015, 2, 4)
    max_volunteer = 0
    max_commitments = 0

    class Meta:
        model = sched.Event


class ResourceAllocationFactory(DjangoModelFactory):
    event = SubFactory(SchedEventFactory)
    resource = SubFactory(WorkerFactory)

    class Meta:
        model = sched.ResourceAllocation


class OrderingFactory(DjangoModelFactory):
    order = Sequence(lambda x: x)
    allocation = SubFactory(ResourceAllocationFactory)

    class Meta:
        model = sched.Ordering


class LabelFactory(DjangoModelFactory):
    text = Sequence(lambda x: "Label #%d" % x)
    allocation = SubFactory(ResourceAllocationFactory)

    class Meta:
        model = sched.Label


class EventContainerFactory(DjangoModelFactory):
    parent_event = SubFactory(SchedEventFactory)
    child_event = SubFactory(SchedEventFactory)

    class Meta:
        model = sched.EventContainer


class EventLabelFactory(DjangoModelFactory):
    text = Sequence(lambda x: "Label #%d" % x)
    event = SubFactory(SchedEventFactory)

    class Meta:
        model = sched.EventLabel


class EventEvalQuestionFactory(DjangoModelFactory):
    question = Sequence(lambda x: "Question #%d" % x)
    order = Sequence(lambda x: x)
    answer_type = "grade"

    class Meta:
        model = sched.EventEvalQuestion


class EventEvalGradeFactory(DjangoModelFactory):
    question = SubFactory(EventEvalQuestionFactory)
    profile = SubFactory(ProfileFactory)
    event = SubFactory(SchedEventFactory)
    answer = 2

    class Meta:
        model = sched.EventEvalGrade


class EventEvalBooleanFactory(DjangoModelFactory):
    question = SubFactory(EventEvalQuestionFactory, answer_type="boolean")
    profile = SubFactory(ProfileFactory)
    event = SubFactory(SchedEventFactory)
    answer = True

    class Meta:
        model = sched.EventEvalBoolean


class EventEvalCommentFactory(DjangoModelFactory):
    question = SubFactory(EventEvalQuestionFactory, answer_type="text")
    profile = SubFactory(ProfileFactory)
    event = SubFactory(SchedEventFactory)
    answer = Sequence(lambda x: "Answer #%d" % x)

    class Meta:
        model = sched.EventEvalComment
