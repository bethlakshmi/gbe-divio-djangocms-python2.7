from tests.factories.scheduler_factories import (
    EventLabelFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory
)
from tests.factories.gbe_factories import ConferenceFactory
from gbetext import calendar_for_event
from datetime import (
    datetime,
    time
)


def book_worker_item_for_role(workeritem, role, conference=None):
    worker = WorkerFactory.create(
        _item=workeritem,
        role=role)
    event = SchedEventFactory()

    if conference is not None:
        EventLabelFactory(
            event=event,
            text=conference.conference_slug
        )
    else:
        EventLabelFactory(
            event=event,
            text=ConferenceFactory().conference_slug
        )
    EventLabelFactory(
        event=event,
        text=calendar_for_event[event.event_style]
    )
    booking = ResourceAllocationFactory.create(
        event=event,
        resource=worker
    )
    return booking


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0))
