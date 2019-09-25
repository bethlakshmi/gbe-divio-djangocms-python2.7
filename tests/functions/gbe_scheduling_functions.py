from tests.factories.scheduler_factories import (
    ActResourceFactory,
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
    event_type_options,
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
        return booking


def get_sched_event_form(context, room=None):
    room = room or context.room
    form_dict = {'event-day': context.days[0].pk,
                 'event-time': "12:00:00",
                 'event-location': room.pk,
                 'event-max_volunteer': 3,
                 'event-e_title': 'New Title',
                 'event-duration': '1:00:00',
                 'event-e_description': 'New Description'}
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


def assert_good_sched_event_form_wizard(response, eventitem):
    assert response.status_code is 200
    if eventitem.__class__.__name__ == "Class":
        for label, detail in [
                (classbid_labels['schedule_constraints'], ', '.join(
                    [j for i, j in class_schedule_options
                     if i in eventitem.schedule_constraints])),
                (classbid_labels['avoided_constraints'], ', '.join(
                    [j for i, j in class_schedule_options
                     if i in eventitem.avoided_constraints])),
                ('Space Needs', eventitem.get_space_needs_display())]:
            assert_label(response, label, detail)


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0, tzinfo=pytz.utc))


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


def assert_event_was_picked_in_wizard(response, event_type):
    checked_button = ""
    x = 0
    for header in event_type_options:
        y = 0
        for subitem in header[1]:
            if event_type == subitem[0]:
                checked_button = (
                    '<input type="radio" name="event_type" value="%s"' +
                    ' required checked id="id_event_type_%d_%d" />') % (
                    event_type, x, y)
            y += 1
        x += 1
    assert '<a data-toggle="collapse" href="#collapse1">' in response.content
    assert checked_button in response.content


def assert_role_choice(response, role_type):
    assert '<option value="%s" selected="selected">%s</option>' % (
        role_type,
        role_type) in response.content
