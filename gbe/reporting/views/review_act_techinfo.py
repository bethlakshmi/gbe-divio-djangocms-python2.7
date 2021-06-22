from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.functions import (
    conference_slugs,
    get_conference_by_slug,
    validate_perms,
)
from gbe.models import (
    Act,
    GenericEvent,
    Show,
)
from scheduler.idd import (
    get_people,
    get_schedule
)
from gbe.scheduling.views.functions import show_general_status


@never_cache
def review_act_techinfo(request, show_id=None):
    '''
    Show the list of act tech info for all acts in a given show
    '''
    validate_perms(
        request,
        ('Scheduling Mavens',
         'Stage Manager',
         'Tech Crew',
         'Technical Director',
         'Producer'))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.
    show = None
    acts = []
    columns = None
    scheduling_link = ''

    if show_id:
        columns = ['Order',
                   'Act',
                   'Performer',
                   'Rehearsal',
                   'Music',
                   'Action']
        show = get_object_or_404(Show, eventitem_id=show_id)
        response = get_people(foreign_event_ids=[show.eventitem_id],
                              roles=["Performer"])
        show_general_status(request, response, "ReviewActTechinfo")
        for performer in response.people:
            rehearsals = []
            order = -1
            act = get_object_or_404(
                Act,
                pk=performer.commitment.class_id)
            sched_response = get_schedule(
                labels=[act.b_conference.conference_slug],
                commitment=act)
            show_general_status(request, sched_response, "ReviewActTechinfo")
            for item in sched_response.schedule_items:
                if item.event not in rehearsals and (
                        GenericEvent.objects.filter(
                            eventitem_id=item.event.eventitem.eventitem_id,
                            type='Rehearsal Slot').exists()):
                    rehearsals += [item.event]
                elif Show.objects.filter(
                        eventitem_id=item.event.eventitem.eventitem_id
                        ).exists():
                    order = item.commitment.order
            acts += [{'act': act, 'rehearsals': rehearsals, 'order': order}]
        if validate_perms(request, ('Scheduling Mavens',), require=False):
            scheduling_link = reverse(
                'schedule_acts',
                urlconf='gbe.scheduling.urls',
                args=[show.pk])

    if show:
        conference = show.e_conference
    else:
        conf_slug = request.GET.get('conf_slug', None)
        conference = get_conference_by_slug(conf_slug)

    return render(request,
                  'gbe/report/act_tech_review.tmpl',
                  {'this_show': show,
                   'acts': acts,
                   'columns': columns,
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
