from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.shortcuts import render
from gbe.reporting.functions import prep_act_tech_info
from gbe_logging import logger
from gbe.functions import (
    conference_slugs,
    get_conference_by_slug,
    validate_perms,
)
from gbe.models import Show

@never_cache
def review_act_techinfo(request, show_id=None):
    '''
    Show the list of act tech info for all acts in a given show
    '''
    validate_perms(
        request,
        ('Scheduling Mavens','Tech Crew', 'Technical Director', 'Producer'))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.
    show = None
    acts = []
    scheduling_link = ''

    if show_id:
        try:
            show = Show.objects.get(eventitem_id=show_id)
            acts = show.scheduler_events.first().get_acts(status=3)
            acts = sorted(acts, key=lambda act: act.order)
            if validate_perms(
                    request, ('Scheduling Mavens',), require=False):
                scheduling_link = reverse(
                    'schedule_acts',
                    urlconf='gbe.scheduling.urls',
                    args=[show.pk])

        except:
            logger.error("review_act_techinfo: Invalid show id")
            pass
    if show:
        conference = show.e_conference
    else:
        conf_slug = request.GET.get('conf_slug', None)
        conference = get_conference_by_slug(conf_slug)

    return render(request,
                  'gbe/report/act_tech_review.tmpl',
                  {'this_show': show,
                   'acts': acts,
                   'all_shows': Show.objects.filter(e_conference=conference),
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'scheduling_link': scheduling_link,
                   'change_acts': validate_perms(
                        request,
                        ('Technical Director', 'Producer'),
                        False),
                   'return_link': reverse('act_techinfo_review',
                                          urlconf='gbe.reporting.urls',)})
