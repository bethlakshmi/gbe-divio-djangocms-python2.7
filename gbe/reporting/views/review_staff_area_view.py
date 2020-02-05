from django.shortcuts import render
from gbe.models import (
    AvailableInterest,
    Conference,
    StaffArea,
    Show,
)
from gbe.functions import (
    conference_slugs,
    validate_perms,
)


def review_staff_area_view(request):
    '''
      Shows listing of staff area stuff for drill down
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()

    header = ['Area', 'Leaders', 'Check Staffing']

    return render(
        request,
        'gbe/report/staff_areas.tmpl',
        {'header': header,
         'areas': StaffArea.objects.filter(conference=conference),
         'shows': Show.objects.filter(e_conference=conference),
         'conference_slugs': conference_slugs(),
         'conference': conference})
