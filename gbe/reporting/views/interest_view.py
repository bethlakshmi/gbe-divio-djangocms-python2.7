from django.shortcuts import render
from django.views.decorators.cache import never_cache
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from django.core.urlresolvers import reverse
from scheduler.idd import get_occurrences
from gbe.models import (
    Class,
    Performer,
    UserMessage,
)
from settings import GBE_DATETIME_FORMAT
from gbetext import interested_report_explain_msg


@never_cache
def interest_view(request):
    viewer_profile = validate_perms(request, 'any', require=True)

    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference()

    response = get_occurrences(
        labels=[conference.conference_slug, "Conference"])
    header = ['Class',
              'Teacher',
              'Location',
              'Max attendees',
              'Style',
              'Interested',
              'Action']

    display_list = []
    events = Class.objects.filter(e_conference=conference)
    for occurrence in response.occurrences:
        class_event = events.get(
                eventitem_id=occurrence.eventitem.eventitem_id)
        teachers = []
        interested = []
        for person in occurrence.people:
            if person.role == "Interested":
                interested += [person]
            elif person.role in ("Teacher", "Moderator"):
                teachers += [Performer.objects.get(pk=person.public_id)]

        display_item = {
            'id': occurrence.id,
            'sort_start': occurrence.start_time,
            'start':  occurrence.start_time.strftime(GBE_DATETIME_FORMAT),
            'title': class_event.e_title,
            'location': occurrence.location,
            'teachers': teachers,
            'eventitem_id': class_event.eventitem_id,
            'interested': interested,
            'type': class_event.type,
            'maximum_enrollment': class_event.maximum_enrollment,
            'detail_link': reverse(
                'detail_view',
                urlconf='gbe.scheduling.urls',
                args=[class_event.eventitem_id])}
        display_list += [display_item]

    display_list.sort(key=lambda k: k['sort_start'])
    user_message = UserMessage.objects.get_or_create(
        view="InterestView",
        code="ABOUT_INTERESTED",
        defaults={
            'summary': "About Interested Attendee Report",
            'description': interested_report_explain_msg})
    return render(request,
                  'gbe/report/interest.tmpl',
                  {'header': header,
                   'classes': display_list,
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'about': user_message[0].description})
