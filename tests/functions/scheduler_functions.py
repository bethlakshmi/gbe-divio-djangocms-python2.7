from tests.factories.scheduler_factories import (
    ActResourceFactory,
    EventLabelFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory
)
from datetime import (
    datetime,
    time
)
import pytz
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
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
        resource=ActResourceFactory.create(
            _item=actitem))
    EventLabelFactory(
        event=booking.event,
        text=eventitem.e_conference.conference_slug
    )
    EventLabelFactory(
        event=booking.event,
        text=eventitem.calendar_type
    )
    return booking


def get_sched_event_form(context, room=None):
    room = room or context.room
    form_dict = {'event-day': context.days[0].pk,
                 'event-time': "12:00:00",
                 'event-location': room.pk,
                 'event-max_volunteer': 3,
                 'event-title': 'New Title',
                 'event-duration': '1:00:00',
                 'event-description': 'New Description'}
    return form_dict


def assert_good_sched_event_form(response, eventitem):
    assert response.status_code is 200
    assert eventitem.e_title in response.content
    assert eventitem.e_description in response.content
    assert '<input id="id_event-duration" name="event-duration" ' + \
        'type="text" value="01:00:00" />' in response.content
    if eventitem.__class__.__name__ == "Class":
        for label, detail in [
                (classbid_labels['schedule_constraints'], ', '.join(
                    [j for i, j in class_schedule_options
                     if i in eventitem.schedule_constraints])),
                (classbid_labels['avoided_constraints'], ', '.join(
                    [j for i, j in class_schedule_options
                     if i in eventitem.avoided_constraints])),
                ('Format', eventitem.type),
                ('Space Needs', eventitem.get_space_needs_display())]:
            assert_label(response, label, detail)


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0))


def assert_selected(response, value, display):
    selection = '<option value="%s" selected="selected">%s</option>' % (
        value,
        display)
    assert selection in response.content


def assert_link(response, link):
    selection = '<a href="%s">' % link
    assert selection in response.content


def assert_label(response, label, details):
    selection = '<label class="sched_detail">%s:</label></br>%s</br></br>' % (
        label,
        details
    )
    assert selection in response.content
