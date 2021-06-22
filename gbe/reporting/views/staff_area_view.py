from django.shortcuts import render
from django.shortcuts import get_object_or_404
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import (
    Conference,
    StaffArea,
)
from gbetext import role_commit_map
from django.urls import reverse


def staff_area_view(request, parent_type, target):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, (
        'Act Coordinator',
        'Class Coordinator',
        'Costume Coordinator',
        'Vendor Coordinator',
        'Volunteer Coordinator',
        'Tech Crew',
        'Scheduling Mavens',
        'Stage Manager',
        'Staff Lead',
        'Ticketing - Admin',
        'Registrar',
        ), require=True)
    other = "Potential"
    roles = []
    if 'filter' in list(request.GET.keys()) and (
            request.GET['filter'] == "Potential"):
        other = "Committed"
    for role, commit in list(role_commit_map.items()):
        if commit[0] == 1 or (
                commit[0] > 0 and commit[0] < 4 and other == "Committed"):
            roles += [role]
    opps_response = None
    area = None
    opps = None
    conference = None
    edit_link = None
    if parent_type == "area":
        area = get_object_or_404(StaffArea, pk=target)
        opps_response = get_occurrences(labels=[
            area.conference.conference_slug,
            area.slug])
        conference = area.conference
        if area.conference.status != 'completed':
            edit_link = reverse("edit_staff",
                                urlconf='gbe.scheduling.urls',
                                args=[area.pk])
    elif parent_type == "event":
        parent_response = get_occurrences(foreign_event_ids=[target])
        if parent_response.occurrences:
            area = parent_response.occurrences[0]
            opps_response = get_occurrences(
                parent_event_id=parent_response.occurrences[0].pk)
            conference = Conference.objects.filter(
                conference_slug__in=area.labels).first()
            if conference.status != 'completed':
                edit_link = reverse(
                    "edit_event",
                    urlconf='gbe.scheduling.urls',
                    args=[conference.conference_slug, area.pk])

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
                   'edit_link': edit_link,
                   })
