from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_or_404
from gbe.reporting.functions import prep_act_tech_info
from gbe_logging import logger
from gbe.functions import (
    conference_slugs,
    get_conference_by_slug,
    validate_perms,
)
from gbe.models import Show
from scheduler.idd import get_schedule
from gbe.scheduling.views.functions import show_general_status


@never_cache
def act_techinfo_detail(request, act_id):
    '''
    Show the list of act tech info for all acts in a given show
    '''
    validate_perms(request, ('Technical Director', 'Producer'))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.
    show = None
    act = None

    act = Act.objects.get_or_404(pk=act_id)
    response = get_schedule(labels=[act.b_conference.conference_slug],
                            act=act)
    show_general_status(request, response, self.__class__.__name__)


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
