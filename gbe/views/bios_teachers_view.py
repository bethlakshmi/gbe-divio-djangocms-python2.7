from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from collections import OrderedDict
from scheduler.idd import get_people
from gbe.models import (
    Bio,
    Class,
)
from gbe.functions import (
    get_latest_conference,
    get_conference_by_slug,
    conference_list,
)


@log_func
def BiosTeachersView(request):
    '''
    Display the teachers bios.  Teachers are anyone teaching,
    moderating or being a panelist.
    '''
    conf_slug = request.GET.get('conference', None)
    if not conf_slug:
        conference = get_latest_conference()
    else:
        conference = get_conference_by_slug(conf_slug)
    conferences = conference_list()
    performers = Bio.objects.all()
    bid_classes = Class.objects.filter(
        b_conference=conference,
        accepted=3)
    bios = {}
    connected_ids = []
    response = get_people(labels=[conference.conference_slug],
                          roles=["Teacher", "Moderator", "Panelist"])

    for performer in response.people:
        connected_ids += [performer.occurrence.connected_id]
        if performer.public_class != "Bio":
            continue
        if performer.public_id not in bios.keys():
            bios[performer.public_id] = {
                'bio': performers.get(pk=performer.public_id),
                'classes': []
            }
        bios[performer.public_id]['classes'] += [{
            'role': performer.role,
            'event': performer.occurrence,
            'detail_id': performer.occurrence.pk}]

    for a_class in bid_classes.exclude(pk__in=connected_ids):
        if a_class.teacher_bio.pk not in bios.keys():
            bios[a_class.teacher_bio.pk] = {
                'bio': a_class.teacher_bio,
                'classes': [],
            }

        bios[a_class.teacher_bio.pk]['classes'] += [{
            'role': "Teacher",
            'event': a_class}]

    template = 'gbe/bio_list.tmpl'
    context = {'bios': OrderedDict(sorted(bios.items(),
                                          key=lambda t: t[1]['bio'].name)),
               'bio_url': reverse('bios_teacher',
                                  urlconf='gbe.urls'),
               'title': 'Conference Bios',
               'conferences': conferences}

    return render(request, template, context)
