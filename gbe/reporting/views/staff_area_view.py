from django.shortcuts import render
from django.shortcuts import get_object_or_404
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea
from gbetext import role_commit_map


def staff_area_view(request, area_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)

    other = "Potential"
    roles = []
    if 'filter' in request.GET.keys() and (
            request.GET['filter'] == "Potential"):
        other = "Committed"
    for role, commit in role_commit_map.items():
        if commit[0] == 1 or (
                commit[0] > 0 and commit[0] < 4 and other == "Committed"):
            roles += [role]
    opps_response = None
    area = None
    opps = None
    conference = None
    try:
        area = StaffArea.objects.get(pk=area_id)
        opps_response = get_occurrences(labels=[
            area.conference.conference_slug,
            area.slug])
        conference = area.conference
    except StaffArea.DoesNotExist:
        parent_response = get_occurrences(foreign_event_ids=[area_id])
        if parent_response.occurrences:
            area = parent_response.occurrences[0]
            opps_response = get_occurrences(
                parent_event_id=parent_response.occurrences[0].pk)
            conference = area.confitem.e_conference

    if opps_response:
        show_general_status(request, opps_response, "staff_area")
        opps = opps_response.occurrences

    return render(request,
                  'gbe/report/staff_area_schedule.tmpl',
                  {'opps': opps,
                   'area': area,
                   'conference': conference,
                   'role_commit_map': role_commit_map,
                   'visible_roles': roles,
                   'other_option': other,
                   })
