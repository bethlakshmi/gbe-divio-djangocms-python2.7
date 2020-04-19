from datetime import (
    datetime,
    time
)
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
    event_type_options,
)


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


def assert_label(response, label, details):
    selection = '<label class="sched_detail">%s:</label></br>%s</br></br>' % (
        label,
        details
    )
    assert bytes(selection, 'utf-8') in response.content


def assert_event_was_picked_in_wizard(response, event_type):
    checked_button = ""
    x = 0
    for header in event_type_options:
        y = 0
        for subitem in header[1]:
            if event_type == subitem[0]:
                checked_button = (
                    '<input type="radio" name="event_type" value="%s"' +
                    ' required id="id_event_type_%d_%d" checked />') % (
                    event_type, x, y)
            y += 1
        x += 1
    assert b'<a data-toggle="collapse" href="#collapse1">' in response.content
    assert bytes(checked_button, 'utf-8') in response.content


def assert_role_choice(response, role_type):
    assert bytes('<option value="%s" selected>%s</option>' % (
        role_type,
        role_type), 'utf-8') in response.content
