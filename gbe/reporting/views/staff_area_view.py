from django.shortcuts import render
from django.shortcuts import get_object_or_404
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea


def staff_area_view(request, area_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    show_style = False
    viewer_profile = validate_perms(request, 'any', require=True)
    if 'area' in request.GET.keys():
        show_style = (request.GET['area'] == "Show")

    opps_response = None
    area = None
    opps = None

    if show_style:
        parent_response = get_occurrences(foreign_event_ids=[area_id])
        if parent_response.occurrences:
            area = parent_response.occurrences[0]
            opps_response = get_occurrences(
                parent_event_id=parent_response.occurrences[0].pk)
    else:
        area = get_object_or_404(StaffArea, pk=area_id)
        opps_response = get_occurrences(labels=[
            area.conference.conference_slug,
            area.slug])
    if opps_response:
        show_general_status(request, opps_response, "staff_area")
        opps = opps_response.occurrences

    return render(request,
                  'gbe/report/staff_area_schedule.tmpl',
                  {'opps': opps,
                   'area': area})
