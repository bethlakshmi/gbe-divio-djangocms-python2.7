from django.views.decorators.cache import never_cache
from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.functions import validate_perms
from gbe.models import (
    Act,
    GenericEvent,
    Show,
)
from scheduler.idd import get_schedule
from gbe.scheduling.views.functions import show_general_status
from gbetext import acceptance_states


@never_cache
def act_techinfo_detail(request, act_id):
    '''
    Show the list of act tech info for all acts in a given show
    '''
    validate_perms(
        request,
        ('Scheduling Mavens','Tech Crew', 'Technical Director', 'Producer'))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.
    shows = []
    rehearsals = []
    act = None
    order = -1

    act = get_object_or_404(Act, pk=act_id)
    if act.accepted == 3:
        response = get_schedule(labels=[act.b_conference.conference_slug],
                                act=act)
        show_general_status(request, response, "ActTechinfoDetail")
        for item in response.schedule_items:
            if item.event not in shows and Show.objects.filter(
                    eventitem_id=item.event.eventitem.eventitem_id).exists():
                shows += [item.event]
                order = item.order
            elif item.event not in rehearsals and GenericEvent.objects.filter(
                    eventitem_id=item.event.eventitem.eventitem_id,
                    type='Rehearsal Slot').exists():
                rehearsals += [item.event]

    return render(request,
                  'gbe/report/act_tech_detail.tmpl',
                  {'act': act,
                   'state': acceptance_states[act.accepted][1],
                   'shows': shows,
                   'order': order,
                   'rehearsals': rehearsals})
