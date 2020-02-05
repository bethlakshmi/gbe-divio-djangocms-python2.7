from django.shortcuts import render
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import (
    AvailableInterest,
    GenericEvent,
)
from django.shortcuts import get_object_or_404


def volunteer_type_view(request, conference_choice, volunteer_type_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    vol_type = get_object_or_404(AvailableInterest, pk=volunteer_type_id)
    eventitem_id_list = GenericEvent.objects.filter(
        e_conference__conference_slug=conference_choice,
        volunteer_type=vol_type).values_list('eventitem_id', flat=True)
    collection = get_occurrences(
        labels=[conference_choice, 'Volunteer'],
        foreign_event_ids=eventitem_id_list)
    show_general_status(request, collection, "volunteer_type")

    return render(request,
                  'gbe/report/staff_area_schedule.tmpl',
                  {'opps': collection.occurrences,
                   'vol_type': vol_type})
