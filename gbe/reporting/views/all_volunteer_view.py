from django.shortcuts import render
from django.shortcuts import get_object_or_404
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import (
    Conference,
    StaffArea,
)
from gbetext import role_commit_map
from django.urls import reverse


def all_volunteer_view(request):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    roles = []
    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference()

    for role, commit in list(role_commit_map.items()):
        if commit[0] > 0 and commit[0] < 4:
            roles += [role]

    opps_response = None
    opps = []
    opps_response = get_occurrences(
        labels=[conference.conference_slug, "Volunteer"])

    if opps_response:
        show_general_status(request, opps_response, "staff_area")
        for opp in opps_response.occurrences:
            item = {
                'event': opp,
                'areas': [],
            }
            for area in StaffArea.objects.filter(slug__in=opp.labels,
                                                 conference=conference):
                item['areas'] += [area]
            opps += [item]

    return render(request,
                  'gbe/report/flat_volunteer_review.tmpl',
                  {'opps': opps,
                   'conference': conference,
                   'conference_slugs': conference_slugs(),
                   'role_commit_map': role_commit_map,
                   'visible_roles': roles,
                   'columns': ['Event',
                               'Parent',
                               'Area',
                               'Date/Time',
                               'Location',
                               'Max',
                               'Current',
                               'Volunteers']
                   })
