from gbe.models import Show
from gbe.functions import (
    get_conference_by_slug,
    validate_perms,
)
from gbe_logging import logger
from django.core.urlresolvers import reverse


def prep_act_tech_info(request, show_id=None):
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

    return show, acts, conference, scheduling_link
