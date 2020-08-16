from tests.factories.scheduler_factories import (
    EventLabelFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory
)
from datetime import (
    datetime,
    time
)


def book_worker_item_for_role(workeritem, role, eventitem=None):
    worker = WorkerFactory.create(
        _item=workeritem,
        role=role)
    if eventitem:
        event = SchedEventFactory.create(
            eventitem=eventitem)
    else:
        event = SchedEventFactory.create()

    EventLabelFactory(
        event=event,
        text=event.eventitem.e_conference.conference_slug
    )
    EventLabelFactory(
        event=event,
        text=event.eventitem.calendar_type
    )
    booking = ResourceAllocationFactory.create(
        event=event,
        resource=worker
    )
    return booking


def book_act_item_for_show(actitem, eventitem):
    booking = ResourceAllocationFactory.create(
        event=SchedEventFactory.create(
            eventitem=eventitem),
        resource=WorkerFactory.create(
            _item=actitem.performer,
            role="Performer"))
    order = OrderingFactory(
        allocation=booking,
        class_id=actitem,
        class_name="Act")
    EventLabelFactory(
        event=booking.event,
        text=eventitem.e_conference.conference_slug
    )
    EventLabelFactory(
        event=booking.event,
        text=eventitem.calendar_type
    )
    return booking


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0))
