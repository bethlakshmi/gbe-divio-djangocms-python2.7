from factory import (
    LazyAttribute,
    SubFactory,
    RelatedFactory,
    Sequence
)
from factory.django import DjangoModelFactory
import scheduler.models as sched
from datetime import (
    datetime,
    timedelta,
)
from tests.factories.gbe_factories import UserFactory


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


class PeopleFactory(DjangoModelFactory):
    class Meta:
        model = sched.People


class SchedEventFactory(DjangoModelFactory):
    title = Sequence(lambda x: "Test Event #%d" % x)
    description = LazyAttribute(
        lambda a: "Description for %s" % a.title)
    blurb = LazyAttribute(
        lambda a: "Blurb for %s" % a.title)
    length = timedelta(hours=1)
    starttime = datetime(2015, 2, 4)
    max_volunteer = 0
    max_commitments = 0
    event_style = "Special"

    class Meta:
        model = sched.Event


class ResourceAllocationFactory(DjangoModelFactory):
    event = SubFactory(SchedEventFactory)
    resource = SubFactory(LocationFactory)

    class Meta:
        model = sched.ResourceAllocation


class PeopleAllocationFactory(DjangoModelFactory):
    event = SubFactory(SchedEventFactory)
    people = SubFactory(PeopleFactory)
    role = "Volunteer"

    class Meta:
        model = sched.PeopleAllocation


class OrderingFactory(DjangoModelFactory):
    order = Sequence(lambda x: x)
    people_allocated = SubFactory(PeopleAllocationFactory)

    class Meta:
        model = sched.Ordering


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
    user = SubFactory(UserFactory)
    event = SubFactory(SchedEventFactory)
    answer = 2

    class Meta:
        model = sched.EventEvalGrade


class EventEvalBooleanFactory(DjangoModelFactory):
    question = SubFactory(EventEvalQuestionFactory, answer_type="boolean")
    user = SubFactory(UserFactory)
    event = SubFactory(SchedEventFactory)
    answer = True

    class Meta:
        model = sched.EventEvalBoolean


class EventEvalCommentFactory(DjangoModelFactory):
    question = SubFactory(EventEvalQuestionFactory, answer_type="text")
    user = SubFactory(UserFactory)
    event = SubFactory(SchedEventFactory)
    answer = Sequence(lambda x: "Answer #%d" % x)

    class Meta:
        model = sched.EventEvalComment
