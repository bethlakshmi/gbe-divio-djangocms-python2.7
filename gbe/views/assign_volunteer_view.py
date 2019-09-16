from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe_logging import log_func
from django.http import HttpResponseRedirect
from gbe.functions import (
    get_conf,
    validate_perms,
)
from gbe.models import (
    Event,
    GenericEvent,
    StaffArea,
    Volunteer
)
from scheduler.idd import (
    get_occurrences,
    get_schedule,
)
from gbe.scheduling.views.functions import show_general_status


@login_required
@log_func
def AssignVolunteerView(request, volunteer_id):
    '''
    Show a bid  which needs to be assigned to shifts by the coordinator.
    To show: display useful information about the bid,
    If user is not a coordinator, politely decline to show anything.
    '''
    reviewer = validate_perms(request, ('Volunteer Coordinator',))

    if int(volunteer_id) == 0 and request.method == 'POST':
        volunteer_id = int(request.POST['volunteer'])
    volunteer = get_object_or_404(
        Volunteer,
        id=volunteer_id,
    )
    if not volunteer.is_current:
        return HttpResponseRedirect(reverse(
            'volunteer_view', urlconf='gbe.urls', args=[volunteer_id]))
    conference, old_bid = get_conf(volunteer)

    actionURL = reverse('volunteer_changestate',
                        urlconf='gbe.urls',
                        args=[volunteer_id])

    response = get_occurrences(
        labels=[volunteer.b_conference.conference_slug],
        max_volunteer=1)
    show_general_status(request, response, "AssignVolunteerView")
    rehearsals = GenericEvent.objects.filter(
        type='Rehearsal Slot', e_conference=volunteer.b_conference
        ).values_list('eventitem_id', flat=True)

    sched_response = get_schedule(
            user=volunteer.profile.user_object,
            labels=[volunteer.b_conference.conference_slug, ],
            roles=['Volunteer', ])
    show_general_status(request, sched_response, "AssignVolunteerView")
    booking_ids = []
    for schedule_item in sched_response.schedule_items:
        booking_ids += [schedule_item.event.pk]

    conf_windows = conference.windows()
    volunteer_event_windows = []
    volunteer_events = Event.objects.filter(
        e_conference=volunteer.b_conference)

    for event in response.occurrences:
        if event.foreign_event_id not in rehearsals:
            window = {
                'occurrence': event,
                'window': conf_windows.filter(
                    day__day=event.starttime.date(),
                    start__lte=event.starttime.time(),
                    end__gt=event.starttime.time()).first(),
                'booked': event.pk in booking_ids,
                'eventitem': event.eventitem,
                'staff_areas': StaffArea.objects.filter(
                    conference=conference,
                    slug__in=event.labels.values_list('text', flat=True))
            }
            if hasattr(event, 'container_event'):
                window['parent_event'] = event.container_event.parent_event
            volunteer_event_windows += [window]

    return render(
        request,
        'gbe/assign_volunteer.tmpl',
        {'volunteer': volunteer,
         'interests': volunteer.interest_list,
         'volunteer_event_windows': volunteer_event_windows,
         'actionURL': actionURL,
         'conference': conference,
         'old_bid': old_bid})
