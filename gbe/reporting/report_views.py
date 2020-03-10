# View functions for reporting
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.management import call_command
from django.views.decorators.cache import never_cache

import gbe.models as conf
import scheduler.models as sched
import ticketing.models as tix
import os as os
import csv
from reportlab.pdfgen import canvas

from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from gbe_logging import logger
from settings import GBE_DATETIME_FORMAT
from django.utils.formats import date_format
from gbe.reporting.functions import prep_act_tech_info


def list_reports(request):
    '''
      Shows listing of all reports in this area
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference()
    return render(request,
                  'gbe/report/report_list.tmpl', {
                      'conference_slugs': conference_slugs(),
                      'conference': conference,
                      'return_link': reverse('report_list',
                                             urlconf='gbe.reporting.urls')})


@never_cache
def env_stuff(request, conference_choice=None):
    '''
    Generates an envelope-stuffing report.
    '''
    reviewer = validate_perms(request, ('Registrar',))

    if conference_choice:
        conference = get_conference_by_slug(conference_choice)
    else:
        conference = get_current_conference()

    people = conf.Profile.objects.filter(user_object__is_active=True)
    acts = conf.Act.objects.filter(
        accepted=3,
        b_conference=conference)
    tickets = tix.Transaction.objects.filter(
        ticket_item__bpt_event__conference=conference)
    roles = sched.Worker.objects.filter(
        Q(allocations__event__eventitem__event__e_conference=conference))
    commits = sched.ResourceAllocation.objects.filter(
        Q(event__eventitem__event__e_conference=conference))

    header = ['Badge Name',
              'First',
              'Last',
              'Tickets',
              'Ticket format',
              'Personae',
              'Staff Lead',
              'Volunteering',
              'Presenter',
              'Show']

    person_details = []
    for person in people:
        ticket_list = ""
        staff_lead_list = ""
        volunteer_list = ""
        class_list = ""
        personae_list = ""
        show_list = ""
        ticket_names = ""

        for ticket in tickets.filter(
                purchaser__matched_to_user=person.user_object):
            ticket_list += str(ticket.ticket_item.bpt_event.ticket_style)+", "
            ticket_names += ticket.ticket_item.title+", "

        for lead in roles.filter(role="Staff Lead", _item=person):
            for commit in commits.filter(resource=lead):
                staff_lead_list += str(commit.event.eventitem)+', '

        for volunteer in roles.filter(role="Volunteer", _item=person):
            for commit in commits.filter(resource=volunteer):
                volunteer_list += str(commit.event.eventitem)+', '

        for performer in person.get_performers():
            personae_list += str(performer) + ', '
            for teacher in roles.filter((Q(role="Teacher") |
                                         Q(role="Moderator") |
                                         Q(role="Panelist")) &
                                        Q(_item=performer)):
                for commit in commits.filter(resource=teacher):
                    class_list += (teacher.role +
                                   ': ' +
                                   str(commit.event.eventitem) +
                                   ', ')
            for act in acts.filter(performer=performer):
                for commit in commits.filter(resource__actresource___item=act):
                    show_list += str(commit.event.eventitem)+', '

        person_details.append(
            [person.get_badge_name().encode('utf-8').strip(),
             person.user_object.first_name.encode('utf-8').strip(),
             person.user_object.last_name.encode('utf-8').strip(),
             ticket_names, ticket_list,
             personae_list,
             staff_lead_list,
             volunteer_list,
             class_list,
             show_list])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=env_stuff.csv'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in person_details:
        writer.writerow(row)
    return response


@never_cache
def review_act_techinfo(request, show_id=None):
    '''
    Show the list of act tech info for all acts in a given show
    '''
    validate_perms(request, ('Tech Crew',))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.
    show, acts, conference, scheduling_link = prep_act_tech_info(
        request, show_id)
    return render(request,
                  'gbe/report/act_tech_review.tmpl',
                  {'this_show': show,
                   'acts': acts,
                   'all_shows': conf.Show.objects.filter(
                       e_conference=conference),
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'scheduling_link': scheduling_link,
                   'return_link': reverse('act_techinfo_review',
                                          urlconf='gbe.reporting.urls',)})


def download_tracks_for_show(request, show_id):
    '''
    Refresh the zipped tar of the tracks for this show.
    '''
    show = conf.Show.objects.get(pk=show_id)
    call_command('sync_audio_downloads',
                 show_name=show.e_title,
                 conf_slug=show.e_conference.conference_slug)
    path = show.download_path()
    f = open(path)
    fname = os.path.basename(path)
    response = HttpResponse(f, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="%s"' % fname
    return response


@never_cache
def room_schedule(request, room_id=None):
    viewer_profile = validate_perms(request,
                                    'any',
                                    require=True)

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    if room_id:
        rooms = [get_object_or_404(conf.Room,
                                   resourceitem_id=room_id)]
    else:
        rooms = conf.Room.objects.filter(conferences=conference)

    conf_days = conference.conferenceday_set.all()
    tmp_days = []
    for position in range(0, len(conf_days)):
        tmp_days.append(conf_days[position].day)
    conf_days = tmp_days

    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():

                if current_day in conf_days:
                    room_set += [{'room': room,
                                  'date': current_day,
                                  'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            day_events += [booking]
        if current_day in conf_days:
            room_set += [{'room': room,
                          'date': current_day,
                          'bookings': day_events}]
    return render(request, 'gbe/report/room_schedule.tmpl',
                  {'room_date': room_set,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


@never_cache
def room_setup(request):

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    conf_days = conference.conferenceday_set.all()
    tmp_days = []
    for position in range(0, len(conf_days)):
        tmp_days.append(conf_days[position].day)
    conf_days = tmp_days

    viewer_profile = validate_perms(request, 'any', require=True)
    rooms = conf.Room.objects.filter(conferences=conference)

    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            booking_class = sched.EventItem.objects.get_subclass(
                eventitem_id=booking.eventitem.eventitem_id)

            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():
                if (current_day in conf_days and len(day_events) > 0):
                    room_set += [{'room': room,
                                  'date': current_day,
                                  'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            if booking_class.__class__.__name__ == 'Class':
                day_events += [{'event': booking,
                                'class': booking_class}]
        if (current_day in conf_days and len(day_events) > 0):
            room_set += [{'room': room,
                          'date': current_day,
                          'bookings': day_events}]

    return render(request,
                  'gbe/report/room_setup.tmpl',
                  {'room_date': room_set,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


@never_cache
def export_badge_report(request, conference_choice=None):
    '''
    Export a csv of all badge printing details.
    '''
    reviewer = validate_perms(request, ('Registrar',))

    people = conf.Profile.objects.filter(user_object__is_active=True)

    if conference_choice:
        badges = tix.Transaction.objects.filter(
            ticket_item__bpt_event__badgeable=True,
            ticket_item__bpt_event__conference__conference_slug=(
                conference_choice)
            ).order_by(
                'ticket_item')

    else:
        badges = tix.Transaction.objects.filter(
            ticket_item__bpt_event__badgeable=True
        ).exclude(
            ticket_item__bpt_event__conference__status='completed').order_by(
                'ticket_item')

    # build header, segmented in same structure as subclasses
    header = ['First',
              'Last',
              'username',
              'Badge Name',
              'Badge Type',
              'Date',
              'State']

    badge_info = []
    # now build content - the order of loops is specific here,
    # we need ALL transactions, if they are limbo, then the purchaser
    # should have a BPT first/last name
    for badge in badges:
        for person in people.filter(
                user_object=badge.purchaser.matched_to_user):
            badge_info.append(
                [badge.purchaser.first_name.encode('utf-8').strip(),
                 badge.purchaser.last_name.encode('utf-8').strip(),
                 person.user_object.username,
                 person.get_badge_name().encode('utf-8').strip(),
                 badge.ticket_item.title,
                 badge.import_date,
                 'In GBE'])
        if len(people.filter(
                user_object=badge.purchaser.matched_to_user)) == 0:
            badge_info.append(
                [badge.purchaser.first_name.encode('utf-8').strip(),
                 badge.purchaser.last_name.encode('utf-8').strip(),
                 badge.purchaser.matched_to_user,
                 badge.purchaser.first_name.encode('utf-8').strip(),
                 badge.ticket_item.title,
                 badge.import_date,
                 'No Profile'])

    # end for loop through acts
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=print_badges.csv'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in badge_info:
        writer.writerow(row)
    return response
